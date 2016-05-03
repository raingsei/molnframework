import os
from importlib import import_module
from molnframework.utils._os import upath
from molnframework.core.exception import ImproperlyConfigured

class ServiceConfig (object):

    def __init__(self, service_name,service_module):
        self.name = service_name
        self.module = service_module

        if not hasattr(self,'label'):
            self.label = service_name.rpartition(".")[2]

        if not hasattr(self,'verbose_name'):
            self.verbose_name = self.label.title()

        if not hasattr(self,'address'):
            self.address = service_name.rpartition(".")[2].lower()

        if not hasattr(self, 'path'):
            self.path = self._path_from_module(service_module)

    def _path_from_module(self, module):
        paths = list(getattr(module, '__path__', []))
        if len(paths) != 1:
            filename = getattr(module, '__file__', None)
            if filename is not None:
                paths = [os.path.dirname(filename)]
            else:
                # For unknown reasons, sometimes the list returned by __path__
                # contains duplicates that must be removed (#25246).
                paths = list(set(paths))
        if len(paths) > 1:
            raise ImproperlyConfigured(
                "The app module %r has multiple filesystem locations (%r); "
                "you must configure this app with an AppConfig subclass "
                "with a 'path' class attribute." % (module, paths))
        elif not paths:
            raise ImproperlyConfigured(
                "The app module %r has no filesystem location, "
                "you must configure this app with an AppConfig subclass "
                "with a 'path' class attribute." % (module,))
        return upath(paths[0])

    @classmethod
    def new(cls,service):
        if not isinstance(service,ServiceConfig):
            raise ValueError("Invalid service object")
        cls = getattr(service.module,service.name)
        return cls(service.name,service.module)
      
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
            return cls(cls_name,mod)

        app_module = import_module(cls_name)

        return cls(app_name, app_module)

        



