from __future__ import unicode_literals

import os
from django.core.management import CommandParser as DJANGO_CommandParser

def handle_default_options(options):
    if options.settings:
        os.environ['MOLNFRAMEWORK_SETTINGS_MODULE'] = options.settings
    if options.pythonpath:
        sys.path.insert(0, options.pythonpath)

class CommandParser(DJANGO_CommandParser):
    """
    Wrapper class to use django command parser
    """

    def __init__(self, cmd, **kwargs):
        super(CommandParser,self).__init__(cmd, **kwargs)



