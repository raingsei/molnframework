from __future__ import unicode_literals

import os
import pkgutil
import sys
import functools
from collections import OrderedDict, defaultdict
from importlib import import_module
from django.core.management.base import CommandError
from django.utils.autoreload import check_errors

import molnframework
from molnframework.conf import settings
from molnframework.utils import apps,six
from molnframework.core.exception import ImproperlyConfigured
from molnframework.core.management.base import (
    CommandParser,handle_default_options,color_style,BaseCommand, CommandError)
from molnframework.utils._os import npath, upath
from molnframework.utils.encoding import force_text
#from molnframework.utils.djangotool import server

def find_commands(management_dir):
    command_dir = os.path.join(management_dir, 'commands')
    return [name for _, name, is_pkg in pkgutil.iter_modules([npath(command_dir)])
            if not is_pkg and not name.startswith('_')]

def load_command_class(app_name, name):
    module = import_module('%s.management.commands.%s' % (app_name, name))
    return module.Command()

@functools.lru_cache(maxsize=None)
def get_commands():
    commands = {name: 'molnframework.core' for name in find_commands(upath(__path__[0]))}

    if not settings.configured:
        return commands

    for app_config in reversed(list(apps.get_service_configs())):
        path = os.path.join(app_config.path, 'management')
        commands.update({name: app_config.name for name in find_commands(path)})

    return commands

class AppCommandUtility(object):
    """
    Encapsulate the logic of molnframework commands.
    """

    def __init__(self,argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])
        self.setting_exception = None

    def main_help_text(self,commands_only=False):
        if commands_only:
            usage = sorted(get_commands().keys())
        else:
            usage = [
                "",
                "Type %s help <subcomand>' for help on specific subcommand." % self.prog_name,
                "",
                "Available subcommands:",
                ]
            commands_dict = defaultdict(lambda:[])
            for name,app in six.iteritems(get_commands()):
                if app == 'molnframework.core':
                    app = 'molnframework'
                else:
                    app = app.rpartition('.')[-1]
                commands_dict[app].append(name)
            style = color_style()
            for app in sorted(commands_dict.keys()):
                usage.append("")
                usage.append(style.NOTICE("[%s]" % app))
                for name in sorted(commands_dict[app]):
                    usage.append("    %s" % name)
            # Output an extra note if settings are not properly configured
            if self.setting_exception is not None:
                usage.append(style.NOTICE(
                    "Note that only Molnframework core commands are listed "
                    "as settings are not properly configured (error: %s)."
                    % self.setting_exception))

        return '\n'.join(usage)

    def fetch_command(self, subcommand):
        # Get commands outside of try block to prevent swallowing exceptions
        commands = get_commands()
        try:
            app_name = commands[subcommand]
        except KeyError:
            if os.environ.get('MOLNFRAMEWORK_SETTINGS_MODULE'):
                # If `subcommand` is missing due to misconfigured settings, the
                # following line will retrigger an ImproperlyConfigured exception
                # (get_commands() swallows the original one) so the user is
                # informed about it.
                settings.INSTALLED_APPS
            else:
                sys.stderr.write("No Molnframework settings specified.\n")
            sys.stderr.write("Unknown command: %r\nType '%s help' for usage.\n" %
                (subcommand, self.prog_name))
            sys.exit(1)
        if isinstance(app_name, BaseCommand):
            # If the command is already loaded, use it directly.
            klass = app_name
        else:
            klass = load_command_class(app_name, subcommand)
        return klass
    
    def run (self):
        """
        Run the given command
        """

        try:
            subcommand = self.argv[1]
        except IndexError:
            subcommand = 'help'

        parser = CommandParser(None, usage="%(prog)s subcommand [options] [args]", add_help=False)
        parser.add_argument('--settings')
        parser.add_argument('--pythonpath')
        parser.add_argument('args', nargs='*')  # catch-all

        try:
            options,args = parser.parse_known_args(self.argv[2:])
            handle_default_options(options)
        except CommandError:
            pass # Ignore any option errors at this point.

        no_settings_commands = [
            'help', 'version', '--help', '--version', '-h',
            'startapp'
        ]

        try:
            settings.INSTALLED_SERVICES
        except ImproperlyConfigured as exc:
            self.setting_exception = exc

            if subcommand in no_settings_commands:
                settings.configure()
        
        if settings.configured:
            if subcommand == 'runapp' not in self.argv:
                try:
                    check_errors(molnframework.setup)()
                except Exception:
                    apps.ready = True
            else:
                molnframework.setup()

        #server.start()

        # TODO: activate command system once the framework is stable

        if subcommand == 'help':
            if '--commands' in args:
                sys.stdout.write(self.main_help_text(commands_only=True) + '\n')
            elif len(options.args) < 1:
                sys.stdout.write(self.main_help_text() + '\n')
            else:
                self.fetch_command(options.args[0]).print_help(self.prog_name, options.args[0])
        elif subcommand == 'version' or self.argv[1:] == ['--version']:
            sys.stdout.write(molnframework.get_version() + '\n')
        elif self.argv[1:] in (['--help'], ['-h']):
            sys.stdout.write(self.main_help_text() + '\n')
        else:
            self.fetch_command(subcommand).run_from_argv(self.argv)

def execute_command_line(argv=None):
    """
    A wrapper method that runs the app command utility
    """

    utility = AppCommandUtility(argv)
    utility.run()







