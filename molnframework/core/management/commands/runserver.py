from __future__ import unicode_literals

from molnframework.conf import settings
from molnframework.utils.djangotool import server
from molnframework.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Start the web services server."

    def add_arguments(self, parser):
        pass

    def execute(self, *args, **options):
        server.start()

    def handle (self, *args, **options):
        pass





