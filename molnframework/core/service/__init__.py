import re
import six
from datetime import datetime
from functools import lru_cache
from collections import OrderedDict
from django.conf.urls import url
from django.http import HttpRequest,HttpResponse
from django.http import Http404

from molnframework.utils.config import ServiceConfig
from molnframework.utils import apps
from molnframework.core.service.parameter import ParameterType,ParameterInfo,ParameterMeta
from molnframework.core.service.result import ExecutionResult
from molnframework.core.exception import ImproperlyConfigured
from molnframework_server.urls import urlpatterns
from molnframework.core.service.base import ServiceBase


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
                    raise ImproperlyConfigured(
                        '"%s" is not a valid regular expression: %s' %
                        (self._regex, six.text_type(e))
                    )
        return self._compiled_reg

    @classmethod
    def get_resolver(cls):
         return cls(r'^/')

class ServiceDecorator (object):
    regexp_lookup = {
        ParameterType.Integer:'(-?\d+$)',
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

    def get_meta (self):
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
        try:
            start = datetime.utcnow() 
            result = service.execute()
            end = datetime.utcnow()

            return ExecutionResult(result,start,end)

        except:
            raise ServiceExecuteException("Execute service contains errors!")


class ServiceManager (object):

    def __init__(self):
        self.registered_services = OrderedDict()

    def _get_response(self,*args):
        assert isinstance(args[0], HttpRequest)

        request = args[0]
        resolver = ServiceLabelResolver.get_resolver()
        path = request.path_info
        match = resolver.regex.search(path)

        if match:
            new_path = path[match.end():]

            for lable,decorated_service in self.registered_services.items():
                if not decorated_service.resolve(new_path):
                    continue

                service_values  = None
                if len(args) > 1:
                    service_values = args[1:]

                    result  = decorated_service.execute(request,service_values)


        return HttpResponse("Hello,world jdfffjdj")

    def register_services (self):

        apps.check_services_ready()

        def get_response(*args): 
            return HttpResponse("Hello,world jdfffjdj")
        
        for service in apps.get_service_configs():

            decorated_service = ServiceDecorator(service)
            url_pattern = decorated_service.get_url_pattern()
            label = decorated_service.get_label()
            
            self.registered_services[label] = decorated_service
            urlpatterns.append(
                url(url_pattern,self._get_response,
                    name=decorated_service.get_name()))

manager = ServiceManager()