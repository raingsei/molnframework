#!/usr/bin/evn python
""" 
Command-line utility for administrative task
"""

import os
import sys

if __name__ == "__main__":

    os.environ.setdefault("MOLNFRAMEWORK_SETTINGS_MODULE","sample.settings")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "molnframework_server.settings")

    import django
    from molnframework.core.management import execute_command_line
    from molnframework.core.management import AppCommandUtility
    from django.core.management import execute_from_command_line
    from django.conf import settings
    from django.apps import apps
    from django.conf.urls import url
    from django.contrib import admin
    from sample.rhino import func1
    from molnframework_server.urls import urlpatterns
    
    urlpatterns.append(url(r'^test/',func1.func1,name="index"))
    execute_from_command_line(sys.argv)
   
    



