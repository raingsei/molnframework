import time
import threading
import json
import socket
from molnframework.utils.client import Client
from molnframework.utils.system import SystemInfo
from molnframework.core.service.metadata import ServiceMetadata,PodMetaData
from molnframework.conf import settings

class HealthReport(object):
    def __init__(self,pod_id,address,port):
        self._pod_id = pod_id
        self._conn = Client(address,port)
        self._event = threading.Event()
        self._thread = None
        
        self._builder = dict()
        self._builder['pod_id'] = self._pod_id

    def get_health(self):
        self._builder['pod_data'] = SystemInfo.get_system_info()
        return json.dumps(self._builder)
        

    def _report(self):

        error_count = 0
        error_message = ""
        error = False
        while not self._event.is_set() and not error:
            result = self._conn.post("/report_pod_health/",self.get_health(),content_type='application/json')
            if result['status'] == "0":
                error_count += 1
                error_message = result["message"]

                if error_count > settings.HEALTH_MAX_REPORT_ERROR:
                    error = True
                    break

            time.sleep(settings.HEALTH_INTEVAL_TIME)
        
        if error:
            raise Exception("Health report encounter errors: %s" % error_message)

        if self._event.is_set():
            self._event.clear()

    def start(self):
        self._thread = threading.Thread(target=self._report)
        
        # start the thread
        self._thread.start()

    def stop(self):
        if self._thread is None:
            return
        self._event.set()
        self._thread = None

class ManagerConnector(object):
    def __init__(self,address,port):
        self.address = address
        self.port = port
        self._conn = Client(address,port)
        self._registered_pod = False

        if port is None:
            self.full_address = self.address
        else:
            self.full_address = "%s:%s" % (self.address,self.port)

    def register_pod(self):
        
        if self._registered_pod:
            return

        settings.BINDED_HOST = settings.HOST
        if settings.HOST == "0.0.0.0":
            settings.BINDED_HOST = socket.gethostbyname(socket.gethostname())

        meta = PodMetaData(settings.BINDED_HOST,settings.PORT).get()

        retry_count = 0
        message = ""
        while not self._registered_pod and retry_count < settings.MAX_RETRY:
            result = self._conn.post("/register_pod/",meta,content_type='application/json')
            
            # TODO
            # Use standard status enumeration not the string
            # it is okay for now

            if result['status'] == "1":
                self._registered_pod = True
                settings.COMPUTE_POD_ID = result['data']['pod_id']
                break

            message = result["message"]
            retry_count +=1
            time.sleep(settings.INTEVAL_TIME)

        if retry_count >= settings.MAX_RETRY:
            raise Exception("Unable to register pod with the last message: %s" % message)            

    def register_service(self,service):

        # get meta from service
        meta = ServiceMetadata(service).get()

        retry_count = 0
        message = ""
        while retry_count < settings.MAX_RETRY:
            result = self._conn.post("/register_service/",meta,content_type='application/json')
            
            # TODO
            # Use standard status enumeration not the string
            # it is okay for now

            if result['status'] == "1":
                break

            message = result["message"]
            retry_count +=1
            time.sleep(settings.INTEVAL_TIME)

        if retry_count >= settings.MAX_RETRY:
            raise Exception("Unable to register pod with the last message: %s" % message)
   
  




