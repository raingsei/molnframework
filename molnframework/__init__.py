from __future__ import unicode_literals
from django.utils.version import get_version

VERSION = (0,0,1,'alpha',0)

__version__ = get_version(VERSION)

def setup():

    from molnframework.utils import apps
    from molnframework.conf import settings
    
    apps.populate(settings.INSTALLED_SERVICES)