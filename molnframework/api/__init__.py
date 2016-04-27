import json
from collections import OrderedDict
from urllib.parse import urlparse
from . import models
from molnframework.utils.client import Client,JSONReponse
from molnframework.core.service.result import ExecutionResult

class APIClientException(Exception):
    pass

class RemoteExecutionerException(Exception):
    pass

class RemoteExecutioner(object):
    def __init__(self,url):
        assert isinstance(url,str)

        if url is "":
            raise ValueError("url")

        full_url = url
        if url.find("http://") == -1:
            full_url = "http://%s" % url
        parsed_url = urlparse(full_url)
        if parsed_url.hostname == "":
            raise ValueError("invalid url")
        self.service_path = parsed_url.path
        self._client = Client(parsed_url.hostname,parsed_url.port)
    def execute(self,path):
        try:
            res = self._client.get(path)
        except ConnectionRefusedError as e:
            raise RemoteExecutionerException("Cannot connect to remote address!")

        return JSONReponse(res)

class ServiceExecutioner(RemoteExecutioner):
    def __init__(self,name,url,parameter_info):
        super(ServiceExecutioner,self).__init__(url)

        self.name = name
        self.url = url
        self.parameter_info = parameter_info

    def _validate(self,**kwargs):
        if len(kwargs) != len(self.parameter_info):
            raise ValueError("Invalid number of argument")
        
        p_value = OrderedDict()
        for parameter in self.parameter_info:
            try:
                value = kwargs.pop(parameter.name)
            except KeyError as e:
                raise ValueError("Missing %s parameter" % parameter.name)
            if not self._validate_value_type(parameter.type,value):
                raise ValueError("Invalid parameter type! %s:%s" %(parameter.name,parameter.type))
            
            p_value[parameter.name] = value

        return p_value

    def _build_execution_path(self,parameters):
        assert isinstance(parameters,dict)

        path = "%s" % self.service_path
        for key in parameters:
            path += "%s/%s/" % (key,str(parameters[key]))

        return path


    def _validate_value_type(self,type,value):
        if type == "Double":
            return self._validate_double(value)
        elif type == "Integer":
            return self._validate_integer(value)
        elif type == "String":
            return self._validate_string(value)
        else:
            raise NotImplementedError("")
            
    def _validate_double(self,value):
        return isinstance(value,float)
    def _validate_integer(self,value):
        return isinstance(value,int)
    def _validate_string(self,value):
        return isinstance(value,str)

    def execute(self,**kwargs):

        # validate parameters
        parameters = self._validate(**kwargs)

        # build path
        path = self._build_execution_path(parameters)

        # execute 
        response = super(ServiceExecutioner,self).execute(path)

        # create result 
        return ExecutionResult.create(response[0])

class APIClient(object):
    def __init__(self,host,port):
        self._host = host
        self._port = port
        self._client = Client(host,port)
    
    @property
    def Host(self):
        return self._host

    @property
    def Port(self):
        return self._port

    def GetResource(self,app_name,service_name):
        assert isinstance(app_name,str)
        assert isinstance(service_name,str)

        if app_name is "":
            raise ValueError("Invalid app_name")
        if service_name is "":
            raise ValueError("Invalid service_name")

        # build request
        req = dict()
        req["app_name"] = app_name
        req_body = json.dumps(req)
        
        # submit request
        res = self._client.post("/get_app_resources/",
            req_body,content_type='application/json')

        if not res['status'] is "1":
            raise APIClientException(res['message'])

        app_model = models.ToComputeApp(res['data'])
        services = list()
        for pd in app_model.pods:
            for sv in pd.services:
                if sv.name == service_name:
                    services.append(ServiceExecutioner(sv.name,sv.url,sv.parameters))
        
        return services
   
