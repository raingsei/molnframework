from importlib import import_module
from molnframework.core.exception import ImproperlyConfigured

class ServiceConfig (object):

    def __init__(self, service_name,service_module):
        self.name = service_name
        self.module = service_module

        if not hasattr(self,'label'):
            self.label = service_name.rpartition(".")[2]

        if not hasattr(self,'verbose_name'):
            self.verbose_name = self.label.title()

    @classmethod
    def create(cls,entry):
        """
        Factory that create an service config from an entry in INSTALLED_SERVICE
        """
        try:
            module = import_module(entry)
        except ImportError:
            model = None

            mod_path, _,cls_name = entry.rpartition('.')

            if not mod_path:
                raise
        else:
            return cls(entry,module)
        
        mod = import_module(mod_path)
        try:
            cls = getattr(mod,cls_name)
        except AttributeError:
            if module is None:
                import_module(entry)
            else:
                raise

        if not issubclass(cls,ServiceConfig):
            raise NotImplementedError(
                "'%s' isn't a subclass of ServiceConfig." % entry)

        try:
            app_name = cls.name
        except AttributeError:
            raise ImproperlyConfigured(
                "'%s' must supply a name attribute." % entry)

        app_module = import_module(app_name)

        return cls(app_name,app_module)
        



