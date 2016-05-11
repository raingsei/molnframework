import json
import io
import sys
from collections import OrderedDict
from urllib.parse import urlparse
from urllib.error import HTTPError
from . import models
from molnframework.utils.client import Client,JSONReponse,CookieAwareClient
from molnframework.core.service.result import ExecutionResult

class APIClientPagNotFoundOrUnauthorizedUser(Exception):
    pass

class APIClientLoginErrorException(Exception):
    pass

class APIClientException(Exception):
    pass

class APIMissingCSRFTokenException(Exception):
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

# TODO
# Use only CookieAwareClient

class APIClientOld(object):
    def __init__(self,host,port,username,password):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._client = Client(host,port)
        self._cookieClient = CookieAwareClient(host,port)
        self._is_authenticated = False
        self._csrf_token = ""
        self._session_id = ""

    def _request(self,path,method,data=None,content_type='application/x-www-form-urlencoded'):
        if not self._is_authenticated:
            raise APIClientPagNotFoundOrUnauthorizedUser()

        try:
            response = self._cookieClient.request(path,method,data,content_type)
        except HTTPError as e:
            raise APIClientPagNotFoundOrUnauthorizedUser()

        return response

    
    def Login(self):
        if self._is_authenticated :
            return

        # get the login csrf token
        self._cookieClient.request('login/',"GET")
        for ck in self._cookieClient.cookie_jar:
            if ck.name == "csrftoken":
                self._csrf_token = ck.value
                break
        if self._csrf_token == "":
            raise APIMissingCSRFTokenException()
        
        # prepare login data
        data = {
            'csrfmiddlewaretoken':self._csrf_token,
            'username':self._username,
            'password':self._password,
            'next':'/'
        }

        # login
        self._cookieClient.request('login/',"POST",data)

        # verify login 
        for ck in self._cookieClient.cookie_jar:
            if ck.name == "sessionid":
                self._session_id = ck.value
            if ck.name == "csrftoken":
                self._csrf_token = ck.value

        if self._session_id == "":
            raise APIClientLoginErrorException()
        
        self._is_authenticated = True

    def Logout(self):
        if self._is_authenticated == False:
            return
        try:
            self._cookieClient.request('logout/',"GET")
        except:
            pass
        
        self._session_id = ""
        self._csrf_token = ""
        self._is_authenticated = False
    
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

class APIClient(object):
    def __init__(self,host,port,username,password):
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    def _login(self,client):

        csrf_token = ""
        session_id = ""

        client.request('login/',"GET")
        for ck in client.cookie_jar:
            if ck.name == "csrftoken":
                csrf_token = ck.value
                break
        if csrf_token == "":
            raise APIMissingCSRFTokenException()
        
        # prepare login data
        data = {
            'csrfmiddlewaretoken':csrf_token,
            'username':self._username,
            'password':self._password,
            'next':'/'
        }

        # login
        client.request('login/',"POST",data)

        # verify login 
        for ck in client.cookie_jar:
            if ck.name == "sessionid":
                session_id = ck.value
            if ck.name == "csrftoken":
                csrf_token = ck.value

        if session_id == "":
            raise APIClientLoginErrorException()

        return (csrf_token,session_id)

    def _logout (self,connection):
        assert isinstance(connection,APIConnection)

        try:
            connection.client.request('logout/',"GET")
        except:
            pass
        
        connection.session_id = ""
        connection.csrf_token = ""
        connection.client = None
        connection.close = None
        connection.username = ""
        connection.password = ""

    def connect(self):
        # create connection and login

        connection = APIConnection()
        connection.client = CookieAwareClient(self._host,self._port)
        connection.csrf_token,connection.session_id = self._login(connection.client)
        connection.username = self._username
        connection.password = self._password
        connection.close = lambda: self._logout(connection)

        return connection

class ConnectionBase(object):
    def close(self):
        pass

class APIConnectionException(Exception):
    pass

class APIConnection(ConnectionBase):
    def __init__(self):
        self.client = None
        self.csrf_token = ""
        self.session_id = ""
        
        # TODO
        # Never send username and password

        self.username = ""
        self.password = ""

    def request(self,path,method,data=None,content_type='application/x-www-form-urlencoded'):
        try:
            response = self.client.request(path,method,data,content_type)
        except HTTPError as e:
            raise APIConnectionException(str(e))
        return response

class HandlerBase(object):
    def __init__(self,conn):
        assert isinstance(conn,APIConnection)

        self.conn = conn


class DockerBuildStreamExtractor(object):
    ''' 
    Extract the output from docker build outputs
    It is not the best extractor but just a quick solution
    '''

    STREAM_KEY = "stream"
    STATUS_KEY = "status"
    ERROR_KEY = "error"

    def _is_stream(self,output):
        return DockerBuildStreamExtractor.STREAM_KEY in output
    def _is_status(self,output):
        return DockerBuildStreamExtractor.STATUS_KEY in output
    def _is_error(self,output):
        return DockerBuildStreamExtractor.ERROR_KEY in output

    def Extract(self,output):

        error = False
        errorMessage = ""

        try:
            dic_output = json.loads(output)
            if self._is_stream(dic_output):
                print(dic_output[DockerBuildStreamExtractor.STREAM_KEY])
            elif self._is_status(dic_output):
                txt = ""
                status_description = dic_output[DockerBuildStreamExtractor.STATUS_KEY]

                if "complete" in status_description or "Verifying" in status_description:
                    print ("\n")

            
                if "progressDetail" in dic_output and "id" in dic_output:
                    id = dic_output["id"]
                    prgs = dic_output["progressDetail"]

                    if "current" in prgs and "total" in prgs:
                        current = dic_output["progressDetail"]["current"]
                        total = dic_output["progressDetail"]["total"]

                        txt = "%s:%s [%3.2f%%]" % (status_description, id, current*100/total)
                        print (txt,end="\r")
                    else:
                        txt = "%s:%s" % (status_description, id)
                        print (txt)
                else:
                    txt = status_description
                    print (txt)
            elif self._is_error(dic_output):
                error = True
                if "errorDetail" in dic_output and "message" in dic_output["errorDetail"]:
                    errorMessage = dic_output["errorDetail"]["message"]
                print ("Error: %s" % errorMessage)
            else:
                print (output) 
        except:
            print (output)

        return (error,errorMessage)
                
class DockerImageHandler(HandlerBase):
    ADD_PATH = "docker/add/"
    BUILD_PATH = "docker/build/"

    def __init__(self,conn):
        super(DockerImageHandler,self).__init__(conn)

    def Add(self,name,content,version):

        class DockerImageAddException(Exception):
            pass

        data = dict()
        data['name'] = name
        data['content'] = content
        data['version'] = version

        res = self.conn.request(DockerImageHandler.ADD_PATH,"POST",data,content_type='application/json')
        
        if not res['status'] is "1":
            raise DockerImageAddException(res['message'])

        return res['data']['docker_image_id'] 

    def Build(self,docker_image_id,show_build_outputs = True):

        class DockerImageBuildException(Exception):
            pass

        indata = dict()
        indata['docker_image_id'] = docker_image_id


        begin_build_resp = self.conn.client.request("docker/build/begin/","POST",indata,content_type='application/json')
        if begin_build_resp['status'] != "1":
            raise DockerImageBuildException(begin_build_resp['message'])

        dck_extracotr = DockerBuildStreamExtractor()
        error = False
        errorMessage = ""
        for output in self.conn.client.request_streaming(DockerImageHandler.BUILD_PATH ,"POST",indata,content_type='application/json'):
            err,errmgs = dck_extracotr.Extract(output)
            if err == True and error == False:
                error = err
                errorMessage = errmgs

        indata["docker_image_error"] = str(error)
        indata["docker_image_error_message"] = errorMessage
        end_build_resp = self.conn.client.request("docker/build/end/","POST",indata,content_type='application/json')

        # The logics here are a bit complicated
        if end_build_resp['status'] != "1":
            raise DockerImageBuildException(end_build_resp['message'])
        if error:
            raise DockerImageBuildException(errorMessage) 

    def Push(self,docker_image_id,show_push_outputs = True):

        class DockerImagePushException(Exception):
            pass

        indata = dict()
        indata['docker_image_id'] = docker_image_id

        begin_push_resp = self.conn.client.request("docker/push/begin/","POST",indata,content_type='application/json')
        if begin_push_resp['status'] != "1":
            raise DockerImagePushException(begin_push_resp['message'])

        dck_extracotr = DockerBuildStreamExtractor()
        error = False
        errorMessage = ""
        for output in self.conn.client.request_streaming("docker/push/" ,"POST",indata,content_type='application/json'):
            err,errmgs = dck_extracotr.Extract(output)
            if err == True and error == False:
                error = err
                errorMessage = errmgs

        indata["docker_image_push_error"] = str(error)
        end_push_resp = self.conn.client.request("docker/push/end/","POST",indata,content_type='application/json')
        if end_push_resp['status'] != "1":
            raise DockerImagePushException(end_push_resp['message'])
        if error:
            raise DockerImagePushException(errorMessage) 

    
    def Test(self):
        self.conn.client.request_streaming('test/',"GET")

class ComputeAppHandlerException(Exception):
    pass

class ComputeAppHandler(HandlerBase):

    def __init__(self,conn):
        super(ComputeAppHandler,self).__init__(conn)

    def Add(self,app_name,app_author,app_number_pods):

        indata = dict()
        indata['app_name'] = app_name
        indata['app_author'] = app_author
        indata['app_number_pods'] = app_number_pods

        
        res = self.conn.request("compute_app/add/","POST",indata,content_type='application/json')
        
        if not res['status'] is "1":
            raise ComputeAppHandlerException(res['message'])

        return (res['data']['app_id'],res['data']['app_port'])        

    def create(self,app_name,app_author,app_number_pods,docker_image_name,app_env=dict()):

        indata = dict()
        indata['app_name'] = app_name
        indata['app_author'] = app_author
        indata['app_number_pods'] = app_number_pods
        indata['app_env'] = json.dumps(app_env)
        indata['password'] = self.conn.password
        indata['docker_image_name'] = docker_image_name
        
        res = self.conn.request("compute_app/create/","POST",indata,content_type='application/json')
        
        if not res['status'] is "1":
            raise ComputeAppHandlerException(res['message'])

        return res['data']

    def get_resources(self,app_name,service_name):

        assert isinstance(app_name,str)
        assert isinstance(service_name,str)

        if app_name is "":
            raise ValueError("Invalid app_name")
        if service_name is "":
            raise ValueError("Invalid service_name")

        # build request
        req = dict()
        req["app_name"] = app_name
        
        # submit request
        res = self.conn.request("compute_app/get_resources/","POST",req,content_type='application/json')
        if not res['status'] is "1":
            raise APIClientException(res['message'])

        app_model = models.ToComputeApp(res['data'])
        services = list()
        for pd in app_model.pods:
            for sv in pd.services:
                if sv.name == service_name:
                    services.append(ServiceExecutioner(sv.name,sv.url,sv.parameters))

        return services
        

        
