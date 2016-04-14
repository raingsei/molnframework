from molnframework.utils.client import Client
from molnframework.core.service.metadata import ServiceMetadata


class MannagerConnector(object):
    def __init__(self,address,port):
        self.address = address
        self.port = port
        self._conn = Client(address,port)

    def register_service(self,service):

        # get meta from service
        meta = ServiceMetadata(service).get()

        # register the service
        self._conn.post("/register/",meta,content_type='application/json')

   
  




