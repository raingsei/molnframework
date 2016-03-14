import sys
from collections import OrderedDict

from .config import ServiceConfig
from molnframework.core.exception import ImproperlyConfigured


class Apps(object):
    """
    A registry that stores the configuration of installed services.
    """

    def __init__(self, installed_services=()):
        if installed_services is None and hasattr(sys.modules[__name__],'apps'):
            raise RuntimeError("You must suppy an installed_service argument.")
        self.ready = False
        self.service_configs = OrderedDict()


    def populate(self,installed_services=None):

        if self.ready:
            return
        if self.service_configs:
            raise RuntimeError("populate() isn't reentrant")

        for entry in installed_services:
            if isinstance(entry,ServiceConfig):
                service_config = entry
            else:
                service_config = ServiceConfig.create(entry)
            if service_config.label in self.service_configs:
                raise NotImplementedError(
                    "Service labels aren't unique, "
                    "duplates: %s" % service_config.label)
            self.service_configs[service_config.label] = service_config

apps = Apps(installed_services=None)


