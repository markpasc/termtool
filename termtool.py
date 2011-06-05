import logging
import os.path
import sys

import argparse
from prettytable import PrettyTable
from progressbar import ProgressBar


def subcommand(*args, **kwargs):
    def decor(fn):
        fn._subcommand = (args, kwargs)
        return fn
    return decor


def argument(*args, **kwargs):
    def decor(fn):
        try:
            arguments = fn._arguments
        except AttributeError:
            arguments = fn._arguments = list()
        arguments.append((args, kwargs))
        return fn
    return decor


class PrettierTable(PrettyTable):

    def __init__(self, fields=None, **kwargs):
        PrettyTable.__init__(self, fields, **kwargs)
        for field in fields:
            self.set_field_align(field, 'l')


class TermtoolMetaclass(type):

    def __new__(cls, name, bases, attrs):
        attrs['_subcommands'] = [attr for attr in attrs.itervalues()
            if hasattr(attr, '_subcommand')]
        return super(TermtoolMetaclass, cls).__new__(cls, name, bases, attrs)


class Termtool(object):

    __metaclass__ = TermtoolMetaclass

    progressbar = ProgressBar
    table = PrettierTable

    def _load_config_args(self):
        appname = type(self).__name__.lower()
        filepath = os.path.expanduser('~/.%s' % appname)
        if not os.path.exists(filepath):
            return list()

        with open(filepath, 'r') as config_file:
            config_args = [line.strip('\n') for line in config_file.readlines()]
        return config_args

    def main(self, argv):
        config_args = self._load_config_args()
        args = config_args + argv

        parser = argparse.ArgumentParser(description=getattr(self, 'description', ''))
        parser.set_defaults(verbosity=[2], subcommand='help')
        parser.add_argument('-v', dest='verbosity', action='append_const', const=1, help='be more verbose (stackable)')
        parser.add_argument('-q', dest='verbosity', action='append_const', const=-1, help='be less verbose (stackable)')
        try:
            class_arguments = self._arguments
        except AttributeError:
            pass
        else:
            for arg_args, arg_kwargs in reversed(class_arguments):
                parser.add_argument(*arg_args, **arg_kwargs)

        subparsers = parser.add_subparsers(dest='subcommand', title='subcommands', metavar='COMMAND')

        for command in self._subcommands:
            try:
                about_args, about_kwargs = command._subcommand
            except AttributeError:
                about_args, about_kwargs = (), {}
            if not about_args:
                about_args = (command.__name__,)
            subparser = subparsers.add_parser(*about_args, **about_kwargs)

            subparser.set_defaults(func=command)

            try:
                arguments = command._arguments
            except AttributeError:
                pass
            else:
                for arg_args, arg_kwargs in reversed(arguments):
                    subparser.add_argument(*arg_args, **arg_kwargs)

        args = parser.parse_args(args)

        verbosity = sum(args.verbosity)
        verbosity = 0 if verbosity < 0 else verbosity if verbosity < 4 else 4
        log_level = (logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG)[verbosity]
        logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
        logging.info('Set log level to %s', logging.getLevelName(log_level))

        try:
            args.func(self, args)
        except KeyboardInterrupt:
            return 1

        return 0

    def run(self):
        sys.exit(self.main(sys.argv[1:]))
