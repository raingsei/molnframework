#!/usr/bin/evn python
""" 
Command-line utility for administrative task
"""

import os
import sys
from molnframework.core import serialisers

if __name__ == "__main__":

    """ Just Keep It """

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

    """ ----- """

    #os.environ.setdefault("MOLNFRAMEWORK_SETTINGS_MODULE","sample.settings")
    #from molnframework.core.management import execute_command_line
    #execute_command_line(sys.argv)

    class Inner(object):
        def __init__(self):
            self.C1 = 0
            self.C2 = 1

    class A(object):
        def __init__(self):
            self.A1 = 0
            self.A2 = 1
            self.A3 = 2
            self.C = Inner()

    class B(A):
        def __init__(self):
            super(B,self).__init__()

            self.B1 = 0
            self.B2 = 1
            self.B3 = 2

    objs = [B(),B()]

    json = serialisers.serialise("json",objs)
    ss =serialisers.deserialise("json",json)

    for item in ss:
        print(item)
   