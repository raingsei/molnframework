import re
import socket
import threading
import time
from datetime import datetime
from functools import lru_cache
from collections import OrderedDict
from django.conf.urls import url
from django.http import HttpRequest,HttpResponse
from django.http import Http404

from molnframework.utils.config import ServiceConfig
from molnframework.utils import six
from molnframework.utils import apps
from molnframework.conf import settings
from molnframework.core.service.parameter import ParameterType,ParameterInfo,ParameterMeta
from molnframework.core.service.result import (ExecutionResult,
    ServiceExecutionResult,ServiceExecutionResultError,ServiceExecutionResultOK)
from molnframework.core.exception import ImproperlyConfigured
from molnframework_server.urls import urlpatterns
from molnframework.core.service.base import ServiceBase
from molnframework.core.service.metadata import ServiceMetadata
from molnframework.core.manager.api import ManagerConnector,HealthReport
from molnframework.core import serialisers


class ServiceResolver404(Http404):
    pass

class ServiceExecuteException(Exception):
    pass

class ServiceLabelResolver(object):
    def __init__(self,regex):
        self._regex = regex
        self._compiled_reg = None

    @property
    def regex(self):
        if self._compiled_reg is None:
            try:
                self._compiled_reg = re.compile(self._regex,re.UNICODE)
            except re.error as e:
                    raise ImproperlyConfigured('"%s" is not a valid regular expression: %s' % (self._regex, six.text_type(e)))
        return self._compiled_reg

    @classmethod
    def get_resolver(cls):
         return cls(r'^/')

class ServiceDecorator(object):
    regexp_lookup = {
        ParameterType.Integer:'(-?\d+)',
        ParameterType.Double:'(-?\d*\.{0,1}\d+)',
        ParameterType.String:'(\w)',
        }


    def __init__(self,service):

        if not isinstance(service,ServiceConfig):
            raise ValueError("Invalid service object type")

        self.service = service
        self.meta = ParameterMeta.get_meta(service)
        self.url_pattern = self._build_url_pattern()
        self.resolver = ServiceLabelResolver(self.url_pattern)

    def _build_url_pattern(self):
        
        builder = ""
        for pm in self.meta.data:
            builder += "%s/%s/" % (pm.name,ServiceDecorator.regexp_lookup[pm.type])

        return r'^%s/%s' % (self.service.address , builder)

    def get_meta(self):
        return self.meta

    def get_service(self):
        if self.service.is_single_instance:
            return ServiceConfig.new(self.service)
        else:
            return self.service

    def get_label(self):
        #assert isinstance(service,ServiceBase)
        return self.service.label

    def get_name(self):
        #assert isinstance(service,ServiceBase)
        return self.service.name

    def get_url_pattern(self):
        #assert isinstance(service,ServiceBase)
        return self.url_pattern

    def resolve(self,path):
        match = self.resolver.regex.search(path)
        if match:
            return True
        return False

    def execute(self,request,args):

        # get service object
        service = self.get_service()

        # get meta
        meta = self.get_meta()

        # parse value to the respected field
        ParameterMeta.parse_values(service,meta,args)

        # execute

        start = datetime.utcnow() 
        resultWrapper = ServiceExecutionResult()

        try:
            result = service.execute()
            resultWrapper = ServiceExecutionResultOK(result=result)
        except Exception as e:
            resultWrapper =ServiceExecutionResultError (str(e))
        end = datetime.utcnow()
        resultWrapper.set_execution_time(start,end)

        return resultWrapper


class ServiceManager(object):

    def __init__(self):
        self.registered_services = OrderedDict()

    def _get_response(self,*args):
        assert isinstance(args[0], HttpRequest)

        request = args[0]
        resolver = ServiceLabelResolver.get_resolver()
        path = request.path_info
        match = resolver.regex.search(path)

        resultStr = ""
        if match:
            new_path = path[match.end():]

            for lable,decorated_service in self.registered_services.items():
                if not decorated_service.resolve(new_path):
                    continue

                service_values = None
                if len(args) > 1:
                    service_values = args[1:]

                    # execute the service
                    result = decorated_service.execute(request,service_values)
                    resultStr = serialisers.serialise("json",result)

                    # TODO
                    # This can introduct a middle layer to process the 
                    # result

                    # serialize the service

        return HttpResponse(resultStr,content_type="application/json")

    def _build_app(self):

        apps.check_services_ready()

        def get_response(*args): 
            return HttpResponse("Hello,world jdfffjdj")
        
        for service in apps.get_service_configs():

            decorated_service = ServiceDecorator(service)
            url_pattern = decorated_service.get_url_pattern()
            label = decorated_service.get_label()
            
            self.registered_services[label] = decorated_service
            urlpatterns.append(url(url_pattern,self._get_response,
                    name=decorated_service.get_name()))

    def _check_server(self,address,port):
        
        # TODO
        # There must be a timeout there

        is_ready = False
        while True:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                conn.settimeout(1)
                conn.connect((address,int(port)))
                conn.close()
                is_ready = True
            except:
                pass
            if is_ready:
                break
            else:
                time.sleep(1)


    def _inner_start(self,address,port):

        # make sure the server is ready
        self._check_server(address,port)

        # register services with the manager

        for service in apps.get_service_configs():
            pass
        

    def start(self,address,port):

        # building application
        self._build_app()

        # start background executions
        # TODO 
        # Should this method executed in background thread manner?
        # threading.Thread(target=self._inner_start,args=(address,port)).start()

        if settings.IGNORE_API is False:
            self.connector = ManagerConnector(settings.MANAGER_ADDRESS,settings.MANAGER_PORT)
            self.connector.register_pod()
            for service in apps.get_service_configs():
                self.connector.register_service(service)
            self.health_reporter = HealthReport(settings.COMPUTE_POD_ID,settings.MANAGER_ADDRESS,settings.MANAGER_PORT)
            self.health_reporter.start()

manager = ServiceManager()