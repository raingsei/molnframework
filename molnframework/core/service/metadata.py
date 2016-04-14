from molnframework.conf import settings
from molnframework.core.service.base import ServiceBase
from molnframework.core.service.parameter import ParameterMeta
import json

class ServiceMetadata(object):
    """
    Get meta data for the service
    """

    def __init__(self,service):
        assert isinstance(service, ServiceBase)

        self._service = service
        self._builder = dict()

        # parameter meta
        praw = []
        pmeta = ParameterMeta.get_meta(self._service)
        for parameter in pmeta:
            praw.append({'name':parameter.name, 'type':str(parameter.type)})

        # build information
        self._builder['app_name'] = settings.APP_NAME
        self._builder['service_name'] = service.name
        self._builder['service_verbose_name'] = service.address
        self._builder['service_url'] = "http://%s:%s/%s/" % (settings.HOST,settings.PORT,service.address)
        self._builder['service_parameter_count'] = pmeta.count()
        self._builder['service_parameters'] = praw

    def get(self):
        """ 
        Construct the metadata for service registration
        """

        return json.dumps(self._builder)



