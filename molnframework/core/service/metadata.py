from molnframework.conf import settings
from molnframework.utils.system import SystemInfo
from molnframework.core.service.base import ServiceBase
from molnframework.core.service.parameter import ParameterMeta
import json
import socket

class PodMetaData(object):
    """
    Get pod information
    """

    def __init__(self,address,port):
        self._address = address
        self._port = port
        self._builder = dict()

        if self._port is None:
            self._full_address = self._address
        else:
            self._full_address = "%s:%s" % (self._address,self._port)

        #Build information
        self._builder['app_name'] = settings.APP_NAME
        self._builder['pod_address'] = self._full_address
        self._builder['pod_name'] =socket.gethostname()
        self._builder['pod_info'] = SystemInfo.get_system_info()

    def get(self):
        return json.dumps(self._builder)


class ServiceMetadata(object):
    """
    Get meta data for the service
    """

    def __init__(self,service):
        assert isinstance(service, ServiceBase)

        self._service = service
        self._builder = dict()

        # parameter meta
        praw = list()
        pmeta = ParameterMeta.get_meta(self._service)
        for parameter in pmeta:
            p = dict()
            p['name'] = parameter.name
            p['type'] = str(parameter.type)
            praw.append(p)

        if settings.PORT is None:
            full_address = settings.BINDED_HOST
        else:
            full_address = "%s:%s" % (settings.BINDED_HOST,settings.PORT)

        # build information
        self._builder['app_name'] = settings.APP_NAME
        self._builder['pod_name'] =socket.gethostname()
        self._builder['pod_address'] = full_address
        self._builder['service_name'] = service.name
        self._builder['service_verbose_name'] = service.address
        self._builder['service_url'] = "http://%s/%s/" % (full_address,service.address)
        self._builder['service_parameter_count'] = pmeta.count()
        self._builder['service_parameters'] = json.dumps(praw)

    def get(self):
        """ 
        Construct the metadata for service registration
        """

        return json.dumps(self._builder)



