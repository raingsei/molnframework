import http.client
import urllib.parse
import enum
import json

class RequestBuilder(http.client.HTTPConnection):

    def __init__(self,host,port):
        super(RequestBuilder,self).__init__(host, port)

    def get (self,path,data=''):
        data = {} if data is None else data
        return self.generic('GET',data)

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
