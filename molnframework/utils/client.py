import enum
import json
import urllib
import urllib.parse
import http.client
from http.client import HTTPResponse
from http.cookiejar import CookieJar

class RequestBuilder(http.client.HTTPConnection):

    def __init__(self,host,port):
        super(RequestBuilder,self).__init__(host, port)

    def get (self,path,data='',content_type='application/x-www-form-urlencoded'):
        data = {} if data is None else data
        return self.generic('GET',path,data,content_type)

    def post (self,path,data=None,content_type='application/x-www-form-urlencoded'):
        data = {} if data is None else data
        return self.generic('POST',path,data,content_type)


    def generic(self, method,path, data,
                content_type = 'application/octet-stream'):
        
        if not isinstance(data, str):
            # parse data
            parsed = urllib.parse.urlencode(data)
        else:
            parsed = data

        header = {
            "Content-type": content_type,
            "Accept": "text/plain",
        }

        # send request
        self.request(method,path,parsed,header)

        return self.getresponse()

class RequestResponse(object):
    def __init__(self, raw):
        assert isinstance(raw, http.client.HTTPResponse)
        self._raw = raw

    @property
    def status(self):
        return self._raw.status
      
    @property
    def reason(self):
        return self._raw.reason

    @property
    def date(self):
        return self._raw.getheader("Date")

    @property
    def content_type(self):
        return self._raw.getheader("Content-type")
    
    @property
    def server(self):
        return self._raw.getheader("Server")

    @property
    def x_Frame_options(self):
        return self._raw.getheader("X-Frame-Options")
    
    @property
    def body(self):
        data =  self._raw.read().decode("utf-8")
        return data
        
    @staticmethod
    def create(response):

        assert isinstance(response, http.client.HTTPResponse)
        
        if response.getheader("Content-type") == "application/json":
            return JSONReponse(response)
        else:
            return RequestResponse(response)

class JSONReponse(RequestResponse):
    def __init__(self, raw):
        super(JSONReponse,self).__init__(raw)
        self._dict = json.loads(self.body)

    def __getitem__(self,key):
        if self.status != 200:
            return None
        return self._dict[key]
    
    def keys(self):
        return self._dict.keys()

class Client(RequestBuilder):

    def __init__(self, host, port = None):
        super(Client,self).__init__(host, port)
        
    def get (self,path,data = None):
        """
        Requests a reponse from the server using GET
        """

        return super(Client,self).get(path,data)

        
    def post(self,url,data=None,content_type='application/x-www-form-urlencoded'):
        """
        Requests a reponse from the server using POST
        """
        response = super(Client,self).post(url,data,content_type)
        
        return RequestResponse.create(response)

class CookieAwareClient(object):
    def __init__(self,host,port = None):
        self.host = host
        self.port = port
        self.cookie_jar = CookieJar()

        # prepare opener
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPHandler(),
            urllib.request.HTTPErrorProcessor(),
            urllib.request.HTTPCookieProcessor(self.cookie_jar))
        #urllib.request.install_opener(self._opener)    

    def _build_request (self,path,method,data,content_type='application/x-www-form-urlencoded'):

        if self.port == None:
            full_url = "http://%s/%s" % (self.host,path)
        else:
            full_url = "http://%s:%s/%s" % (self.host,self.port,path)

        headers = {
            "Content-type": content_type,
            "Accept": "text/plain",
        }

        if content_type == 'application/x-www-form-urlencoded':
            parsed_data = None
            if not isinstance(data, str) and data is not None:
                parsed_data = bytes(urllib.parse.urlencode(data).encode('utf-8'))
            else:
                parsed_data = data

            req = urllib.request.Request(full_url,parsed_data,headers,method=method)
        elif content_type == 'application/json':
            req = urllib.request.Request(full_url,headers=headers)
            req.data = bytes(json.dumps(data).encode('utf-8'))
        else:
            raise not NotImplementedError()

        return req

    def request_streaming(self,path,method,data=None,content_type='application/x-www-form-urlencoded'):
        #build the request
        req = self._build_request(path,method,data,content_type)

        with self._opener.open(req) as f:
            while True:
                buffer = f.readline()
                yield buffer.decode('utf-8')
                if not buffer:
                    break

    def request(self,path,method,data=None,content_type='application/x-www-form-urlencoded'):
        req = self._build_request(path,method,data,content_type)
        response = self._opener.open(req)

        return RequestResponse.create(response)
