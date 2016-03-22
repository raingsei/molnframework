#!/usr/bin/evn python
""" 
Command-line utility for administrative task
"""

import os
import sys

if __name__ == "__main__":

    ##os.environ.setdefault("MOLNFRAMEWORK_SETTINGS_MODULE","sample.settings")
    ##from molnframework.core.management import execute_command_line
    ##execute_command_line(sys.argv)
    
    #os.environ.setdefault("DJANGO_SETTINGS_MODULE", "molnframework_server.settings")
    #from django.core.management import execute_from_command_line
    #from django.conf.urls import url
    #from sample.rhino import func1
    #from sample.rhino.func2 import TestFunctionService
    #from molnframework_server.urls import urlpatterns
    #from molnframework.utils import apps
    #from collections import Counter, OrderedDict, defaultdict

    #def test(request):
    #    obj = TestFunctionService()
    #    return TestFunctionService.execute()
    
    ##for service in apps.get_service_configs():
    ##    print (service.address)

    
    #urlpatterns.append(url(r'^test/',test,name="index"))

    #execute_from_command_line(sys.argv)

    os.environ.setdefault("MOLNFRAMEWORK_SETTINGS_MODULE","sample.settings")
    from molnframework.core.management import execute_command_line
    execute_command_line(sys.argv)



