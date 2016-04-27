from __future__ import unicode_literals

import os
from collections import Counter, OrderedDict, defaultdict
from django.conf.urls import url
from django.core.management import execute_from_command_line as django_execute
from molnframework.utils import apps
from molnframework.conf import settings
from molnframework.core.service import manager
from molnframework.core.service.metadata import ServiceMetadata
from molnframework_server.urls import urlpatterns
from threading import Thread
import time


class StartDjangoServerException(Exception):
    pass

def install_service(service_url):
    pass

def test ():
    for i in range(0,100):
        time.sleep(1)
        print (i)

class DjangoServerUtility (object):

    def __init__(self, runserver_argv=None):

        django_argv = "%s runserver" % os.path.basename(__file__)
        if runserver_argv is not None:
            django_argv = django_argv + " " + runserver_argv

        # Arguments for Django server
        self.django_argv = django_argv.split()

        # Mapping installed service lable
        self.installed_services = OrderedDict()


    def _install_services (self):
        pass
        #urlpatterns.append
        #url(r'^test/','sample.rhino.func1')


    def start(self):
        """ start the server """

        # set server settings
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "molnframework_server.settings")

        # start the manager
        manager.start(settings.HOST,settings.PORT)

        #Thread(target=test).start()


        # start server 
        django_execute(self.django_argv)

server = DjangoServerUtility(runserver_argv="%s:%s --noreload --nothreading" % (settings.HOST,settings.PORT))
