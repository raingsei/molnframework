# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import warnings
from argparse import ArgumentParser
from optparse import OptionParser

import molnframework
from molnframework.core import checks
from molnframework.core.management.color import color_style, no_style
from molnframework.utils.encoding import force_str


class CommandError(Exception):
    pass


class SystemCheckError(CommandError):
    pass


class CommandParser(ArgumentParser):
    def __init__(self, cmd, **kwargs):
        self.cmd = cmd
        super(CommandParser, self).__init__(**kwargs)

    def parse_args(self, args=None, namespace=None):
        # Catch missing argument for a better error message
        if (hasattr(self.cmd, 'missing_args_message') and
                not (args or any(not arg.startswith('-') for arg in args))):
            self.error(self.cmd.missing_args_message)
        return super(CommandParser, self).parse_args(args, namespace)

    def error(self, message):
        if self.cmd._called_from_command_line:
            super(CommandParser, self).error(message)
        else:
            raise CommandError("Error: %s" % message)


def handle_default_options(options):
    if options.settings:
        os.environ['MOLNFRAMEWORK_SETTINGS_MODULE'] = options.settings
    if options.pythonpath:
        sys.path.insert(0, options.pythonpath)


class OutputWrapper(object):
    @property
    def style_func(self):
        return self._style_func

    @style_func.setter
    def style_func(self, style_func):
        if style_func and self.isatty():
            self._style_func = style_func
        else:
            self._style_func = lambda x: x

    def __init__(self, out, style_func=None, ending='\n'):
        self._out = out
        self.style_func = None
        self.ending = ending

    def __getattr__(self, name):
        return getattr(self._out, name)

    def isatty(self):
        return hasattr(self._out, 'isatty') and self._out.isatty()

    def write(self, msg, style_func=None, ending=None):
        ending = self.ending if ending is None else ending
        if ending and not msg.endswith(ending):
            msg += ending
        style_func = style_func or self.style_func
        self._out.write(force_str(style_func(msg)))


class BaseCommand(object):
    # Metadata about this command.
    option_list = ()
    help = ''
    args = ''

    # Configuration shortcuts that alter various logic.
    _called_from_command_line = False
    can_import_settings = True
    output_transaction = False  # Whether to wrap the output in a "BEGIN; COMMIT;"
    leave_locale_alone = False
    requires_system_checks = True

    def __init__(self, stdout=None, stderr=None, no_color=False):
        self.stdout = OutputWrapper(stdout or sys.stdout)
        self.stderr = OutputWrapper(stderr or sys.stderr)
        if no_color:
            self.style = no_style()
        else:
            self.style = color_style()
            self.stderr.style_func = self.style.ERROR

    @property
    def use_argparse(self):
        return not bool(self.option_list)

    def get_version(self):
        return molnframework.get_version()

    def usage(self, subcommand):
        usage = '%%prog %s [options] %s' % (subcommand, self.args)
        if self.help:
            return '%s\n\n%s' % (usage, self.help)
        else:
            return usage

    def create_parser(self, prog_name, subcommand):
        if not self.use_argparse:
            def store_as_int(option, opt_str, value, parser):
                setattr(parser.values, option.dest, int(value))

            # Backwards compatibility: use deprecated optparse module
            warnings.warn("OptionParser usage for Django management commands "
                          "is deprecated, use ArgumentParser instead",Exception)
            parser = OptionParser(prog=prog_name,
                                usage=self.usage(subcommand),
                                version=self.get_version())
            parser.add_option('-v', '--verbosity', action='callback', dest='verbosity', default=1,
                type='choice', choices=['0', '1', '2', '3'], callback=store_as_int,
                help='Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output')
            parser.add_option('--settings',
                help=(
                    'The Python path to a settings module, e.g. '
                    '"myproject.settings.main". If this isn\'t provided, the '
                    'MOLNFRAMEWORK_SETTINGS_MODULE environment variable will be used.'
                ),
            )
            parser.add_option('--pythonpath',
                help='A directory to add to the Python path, e.g. "/home/molnframeworkprojects/myproject".'),
            parser.add_option('--traceback', action='store_true',
                help='Raise on CommandError exceptions')
            parser.add_option('--no-color', action='store_true', dest='no_color', default=False,
                help="Don't colorize the command output.")
            for opt in self.option_list:
                parser.add_option(opt)
        else:
            parser = CommandParser(self, prog="%s %s" % (os.path.basename(prog_name), subcommand),
                description=self.help or None)
            parser.add_argument('--version', action='version', version=self.get_version())
            parser.add_argument('-v', '--verbosity', action='store', dest='verbosity', default='1',
                type=int, choices=[0, 1, 2, 3],
                help='Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output')
            parser.add_argument('--settings',
                help=(
                    'The Python path to a settings module, e.g. '
                    '"myproject.settings.main". If this isn\'t provided, the '
                    'MOLNFRAMEWORK_SETTINGS_MODULE environment variable will be used.'
                ),
            )
            parser.add_argument('--pythonpath',
                help='A directory to add to the Python path, e.g. "/home/molnframeworkprojects/myproject".')
            parser.add_argument('--traceback', action='store_true',
                help='Raise on CommandError exceptions')
            parser.add_argument('--no-color', action='store_true', dest='no_color', default=False,
                help="Don't colorize the command output.")
            if self.args:
                # Keep compatibility and always accept positional arguments, like optparse when args is set
                parser.add_argument('args', nargs='*')
            self.add_arguments(parser)
        return parser

    def add_arguments(self, parser):
        pass

    def print_help(self, prog_name, subcommand):
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()

    def run_from_argv(self, argv):
        self._called_from_command_line = True
        parser = self.create_parser(argv[0], argv[1])

        if self.use_argparse:
            options = parser.parse_args(argv[2:])
            cmd_options = vars(options)
            # Move positional args out of options to mimic legacy optparse
            args = cmd_options.pop('args', ())
        else:
            options, args = parser.parse_args(argv[2:])
            cmd_options = vars(options)
        handle_default_options(options)
        try:
            self.execute(*args, **cmd_options)
        except Exception as e:
            if options.traceback or not isinstance(e, CommandError):
                raise

            # SystemCheckError takes care of its own formatting.
            if isinstance(e, SystemCheckError):
                self.stderr.write(str(e), lambda x: x)
            else:
                self.stderr.write('%s: %s' % (e.__class__.__name__, e))
            sys.exit(1)
        finally:
            pass

    def execute(self, *args, **options):
        if options.get('no_color'):
            self.style = no_style()
            self.stderr.style_func = None
        if options.get('stdout'):
            self.stdout = OutputWrapper(options['stdout'])
        if options.get('stderr'):
            self.stderr = OutputWrapper(options.get('stderr'), self.stderr.style_func)

    def handle(self, *args, **options):
        raise NotImplementedError('subclasses of BaseCommand must provide a handle() method')


class AppCommand(BaseCommand):
    missing_args_message = "Enter at least one application label."

    def add_arguments(self, parser):
        parser.add_argument('args', metavar='app_label', nargs='+',
            help='One or more application label.')

    def handle(self, *app_labels, **options):
        from molnframework.utils import apps
        try:
            app_configs = [apps.get_app_config(app_label) for app_label in app_labels]
        except (LookupError, ImportError) as e:
            raise CommandError("%s. Are you sure your INSTALLED_APPS setting is correct?" % e)
        output = []
        for app_config in app_configs:
            app_output = self.handle_app_config(app_config, **options)
            if app_output:
                output.append(app_output)
        return '\n'.join(output)

    def handle_app_config(self, app_config, **options):
        raise NotImplementedError(
            "Subclasses of AppCommand must provide"
            "a handle_app_config() method.")


class LabelCommand(BaseCommand):
    label = 'label'
    missing_args_message = "Enter at least one %s." % label

    def add_arguments(self, parser):
        parser.add_argument('args', metavar=self.label, nargs='+')

    def handle(self, *labels, **options):
        output = []
        for label in labels:
            label_output = self.handle_label(label, **options)
            if label_output:
                output.append(label_output)
        return '\n'.join(output)

    def handle_label(self, label, **options):
        raise NotImplementedError('subclasses of LabelCommand must provide a handle_label() method')


class NoArgsCommand(BaseCommand):
    args = ''

    def __init__(self):
        warnings.warn(
            "NoArgsCommand class is deprecated and will be removed in Django 1.10. "
            "Use BaseCommand instead, which takes no arguments by default.",
            RemovedInDjango110Warning
        )
        super(NoArgsCommand, self).__init__()

    def handle(self, *args, **options):
        if args:
            raise CommandError("Command doesn't accept any arguments")
        return self.handle_noargs(**options)

    def handle_noargs(self, **options):
        raise NotImplementedError('subclasses of NoArgsCommand must provide a handle_noargs() method')
