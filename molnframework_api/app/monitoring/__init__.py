import threading
import django.dispatch

from concurrent.futures import ThreadPoolExecutor
from ..models import ComputeService
from ..models import ComputeApp
from ..events import app_service_registered

def get_health(address):
    pass

class MonitorService(object):
    def start():
        raise NotImplementedError("")
    def stop():
        raise NotImplementedError("")

class HealthMonitorService(MonitorService):
    def get_tasks(self):
        pass


class Monitor(object):
    pool_executor_cls = ThreadPoolExecutor
    max_workers = 4

    def __init__(self):
        app_service_registered.connect(
            receiver=self.on_app_service_register)

        self._has_started = False
        self._services = {
            HealthMonitorService()
        }
       

    def on_app_service_register(self,**kwargs):
        pass

    def add_service(self):
        pass

    def remove_service(self):
        pass

    @property
    def has_started(self):
        return self._has_started

    def start(self):
        self.pool = self.pool_executor_cls(self.max_workers)
        self._has_started = True

        while True:
            for service in self._services:
                pass 
        

monitor = Monitor()