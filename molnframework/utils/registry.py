import sys
from collections import Counter, OrderedDict, defaultdict

from .config import ServiceConfig
from molnframework.core.exception import ServiceRegistryNotReady,ImproperlyConfigured


class Apps(object):
    """
    A registry that stores the configuration of installed services.
    """

    def __init__(self, installed_services=()):
        if installed_services is None and hasattr(sys.modules[__name__],'apps'):
            raise RuntimeError("You must suppy an installed_service argument.")
        self.ready = False
        self.service_configs = OrderedDict()

    def check_services_ready(self):
        """
        Raises an exception if all services haven't been imported yet.
        """
        if not self.ready:
            raise ServiceRegistryNotReady("Services arent's loaded yet.")

    def get_service_configs (self):
        """
        Return an iterable of registered service
        """
        self.check_services_ready()
        return self.service_configs.values()


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
    
        # Check for duplicate service names.
        counts = Counter(
            service_config.name for service_config in self.service_configs.values())
        duplicates = [
                name for name, count in counts.most_common() if count > 1]
        if duplicates:
            raise ImproperlyConfigured(
                "Service names aren't unique, "
                "duplicates: %s" % ", ".join(duplicates))

        # TODO  
        # Validate address name

        self.ready = True

apps = Apps(installed_services=None)


