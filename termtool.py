import logging
import os
import os.path
import sys

import argparse
from prettytable import PrettyTable
from progressbar import ProgressBar


__version__ = '1.1dev'


def subcommand(name=None, **kwargs):
    """Decorate an instance method as a tool subcommand.

    The function's own name is used as the subcommand name for the terminal
    user to type. To use a different one, specify the `name` argument to the
    `subcommand()` decorator.

    The remaining keyword arguments are passed to the `add_parser()` method
    declaring the subcommand, so arguments to the `argparse.ArgumentParser`
    constructor are valid.

    """
    def _decor(fn):
        """Tag the decorated function with the subcommand settings to use later."""
        fn._subcommand = (name or fn.__name__, kwargs)
        return fn
    return _decor


def argument(*args, **kwargs):
    """Declare an argument to the decorated class or instance method.

    The parameters to the `argument()` decorator should specify an argument
    definition as if you were calling `Parser.add_argument()`.

    If decorating a class, the specified argument is a global argument
    available to all subcommands.

    """
    def _decor(fn):
        """Tag the decorated function/class with the argument settings to use later."""
        try:
            arguments = fn._arguments
        except AttributeError:
            arguments = fn._arguments = list()
        arguments.append((args, kwargs))
        return fn
    return _decor


class PrettierTable(PrettyTable):

    def __init__(self, field_names=None, **kwargs):
        PrettyTable.__init__(self, field_names, **kwargs)
        if field_names is not None:
            for field in field_names:
                self.set_field_align(field, 'l')


class _TermtoolMetaclass(type):

    """Metaclass for `Termtool` classes.

    This metaclass automatically sets the ``_subcommands`` class attribute to a
    list of class attributes that have ``_subcommand`` attributes -- that is,
    all the methods decorated with the `subcommand()` decorator.

    """

    def __new__(cls, name, bases, attrs):
        attrs['_subcommands'] = [attr for attr in attrs.itervalues()
            if hasattr(attr, '_subcommand')]
        return super(_TermtoolMetaclass, cls).__new__(cls, name, bases, attrs)


class Termtool(object):

    """A terminal tool for performing actions at a command line.

    Define a new terminal tool by subclassing `Termtool` and decorating its
    instance methods with the `subcommand()` decorator. Use the `argument()`
    decorator too to declare the subcommands' arguments. You can also use the
    `argument()` decorator on your `Termtool` subclass to declare global
    arguments valid for all commands.

    Instantiate your class and call `run()` to run as a command line tool.

    """

    __metaclass__ = _TermtoolMetaclass

    progressbar = ProgressBar
    table = PrettierTable

    def write_config_file(self, *args):
        """Write out a config file containing the given arguments.

        On future command line runs of the tool, the saved command line
        arguments will be used as though the user specified them on the command
        line.

        The arguments are written one per line to the ``~/.toolname`` file,
        where `toolname` is the name of the `Termtool` instance's class, in
        lower case. The file is created if not present and overwritten if it
        is. The file is opened with umask 077 so it is readable only by the
        user invoking the tool (and whose home directory it's written to).

        """
        appname = type(self).__name__.lower()
        filepath = os.path.expanduser('~/.%s' % appname)

        # Don't let anybody else read the config file.
        os.umask(077)
        with open(filepath, 'w') as config_file:
            for arg in args:
                config_file.write(arg)
                config_file.write('\n')

    def read_config_file(self):
        """Read the terminal user's config file for this tool.

        The config file is ``~/.toolname`` where `toolname` is the name of the
        `Termtool` instance's class, in lower case. The method returns a list
        of config arguments as read from the file, one per line.

        """
        appname = type(self).__name__.lower()
        filepath = os.path.expanduser('~/.%s' % appname)
        if not os.path.exists(filepath):
            return list()

        with open(filepath, 'r') as config_file:
            config_args = [line.strip('\n') for line in config_file.readlines()]
        return config_args

    def main(self, argv):
        """Perform the tool's functions, given the specified command line
        arguments.

        This method reads the instance's config file with the
        `read_config_file()` method, adds the arguments specified in `argv`,
        and performs the subcommand identified there.

        The method returns an integer exit code suitable for using with
        `sys.exit()`. That is, `main()` returns ``1`` if the command terminates
        abnormally and ``0`` otherwise. However if ``--help`` or invalid
        arguments are specified, the process is terminated by `argparse`
        instead and `main()` will not return.

        """
        config_args = self.read_config_file()
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
            # Add arguments in the order they were declared.
            for arg_args, arg_kwargs in reversed(class_arguments):
                parser.add_argument(*arg_args, **arg_kwargs)

        subparsers = parser.add_subparsers(dest='subcommand', title='subcommands', metavar='')

        # Add all the subcommands in asciibetical order by command name.
        for command in sorted(self._subcommands, key=lambda c: c._subcommand[0]):
            name, about_kwargs = command._subcommand
            subparser = subparsers.add_parser(name, **about_kwargs)

            # Set the subparser's func so it becomes this command (callable)
            # when the user invokes this subparser.
            subparser.set_defaults(func=command)

            try:
                arguments = command._arguments
            except AttributeError:
                pass
            else:
                # Add arguments in the order they were declared.
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
        """Invoke the terminal command for usage at the command line.

        This method invokes the instance's `main()` method, passing the command
        line arguments specified in `sys.argv`, and terminating the process
        using `sys.exit()` with the exit code returned by `main()`.

        """
        sys.exit(self.main(sys.argv[1:]))
