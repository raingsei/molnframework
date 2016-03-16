from __future__ import unicode_literals

import os
import django
from django.apps import apps
from django.conf import settings
from django.core.management import ManagementUtility
from django.core.exceptions import ImproperlyConfigured

class StartDjangoServerException(Exception):
    pass

class DjangoServerUtility (object):

    def __init__(self, argv=None):
        self.django_manager = ManagementUtility()

    def execute(self,argv=None):
        self.django_manager.execute(argv)

    def start(self):
        
        try:
            settings.INSTALLED_APPS
        except ImproperlyConfigured as exc:
            raise StartDjangoServerException(
                "Invalid installed apps")

        if settings.configured:
            django.setup()

