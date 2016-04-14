import http.client
import urllib.parse
import enum

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
        
        return super(Client,self).post(url,data,content_type)
