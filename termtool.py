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


class _PrettierTable(PrettyTable):

    def __init__(self, field_names=None, **kwargs):
        PrettyTable.__init__(self, field_names, **kwargs)
        try:
            self.set_field_align
        except AttributeError:
            # We must be using PrettyTable 0.6+.
            self.align = 'l'
        else:
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
    table = _PrettierTable

    log_format = '%(levelname)s: %(message)s'
    """The logging format string that `configure_tool()` will configure logging with."""

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
        os.umask(0o077)
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

    class _LogLevelAddAction(argparse.Action):

        """An `argparse` action for selecting a `logging` level."""

        LEVELS = (logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG)

        def __init__(self, option_strings, dest, const, default=None, required=False, help=None, metavar=None):
            # Log level addition actions take no arguments.
            super(Termtool._LogLevelAddAction, self).__init__(nargs=0,
                option_strings=option_strings, dest=dest, const=const, default=default, required=required, help=help)

        def __call__(self, parser, namespace, values, option_string=None):
            level = getattr(namespace, self.dest, logging.WARNING)
            index = self.LEVELS.index(level)
            addend = self.const if self.const is not None else 1
            try:
                level = self.LEVELS[index + addend]
            except IndexError:
                pass
            else:
                setattr(namespace, self.dest, level)

    def build_arg_parser(self):
        """Build and return the `argparse.ArgumentParser` instance suitable for
        parsing arguments for this `Termtool` instance.

        The instance's subcommands and arguments are evaluated, with the
        subcommands added as subparsers. The `ArgumentParser` also supports
        ``-v`` and ``-q`` options for controlling the `logging` module log
        level.

        """
        # Arguments after the subcommand are parsed by the subparser only, so
        # specify the global options in a parent parser so they're valid both
        # before and after the subcommand.
        global_parser = argparse.ArgumentParser(add_help=False)
        global_parser.set_defaults(loglevel=logging.WARNING)
        global_parser.add_argument('-v', dest='loglevel', action=self._LogLevelAddAction, const=1, help='be more verbose (stackable)')
        global_parser.add_argument('-q', dest='loglevel', action=self._LogLevelAddAction, const=-1, help='be less verbose (stackable)')
        try:
            class_arguments = self._arguments
        except AttributeError:
            pass
        else:
            # Add arguments in the order they were declared.
            for arg_args, arg_kwargs in reversed(class_arguments):
                global_parser.add_argument(*arg_args, **arg_kwargs)

        try:
            description = self.description
        except AttributeError:
            description = self.__doc__
        parser = argparse.ArgumentParser(description=description, parents=[global_parser])
        parser.set_defaults(subcommand='help')

        subparsers = parser.add_subparsers(dest='subcommand', title='subcommands', metavar='')

        # Add all the subcommands in asciibetical order by command name.
        for command in sorted(self._subcommands, key=lambda c: c._subcommand[0]):
            name, about_kwargs = command._subcommand
            try:
                description = about_kwargs.pop('description')
            except KeyError:
                description = command.__doc__
            subparser = subparsers.add_parser(name, parents=[global_parser],
                description=description, **about_kwargs)

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

        return parser

    class _NoColorLogFormatter(logging.Formatter):

        def format(self, record):
            record.levelcolor = ''
            record.resetcolor = ''
            return super(Termtool._NoColorLogFormatter, self).format(record)

    class _ColorLogFormatter(logging.Formatter):

        color_for_level = {
            logging.DEBUG:    '32',  # green
            logging.INFO:     '37',  # white
            logging.WARNING:  '33',  # yellow
            logging.ERROR:    '31',  # red
            logging.CRITICAL: '35',  # magenta
        }

        def format(self, record):
            color = self.color_for_level.get(record.levelno)
            if color is not None:
                record.levelcolor = u'\033[1;%sm' % color
            record.resetcolor = u'\033[0m'
            return super(Termtool._ColorLogFormatter, self).format(record)

    def configure_tool(self, args):
        """Configure the tool according to the command line arguments.

        Override this method to configure your tool with the values of any
        other options it supports.

        This implementation configures the `logging` module to the log level
        requested by the user through the ``-v`` and ``-q`` options. It also
        configures logging to go to stderr, formatted according to the
        instance's `log_format` attribute.

        Additionally, logging is configured to provide these additional format
        strings:

        %(levelcolor)s    If stderr is a terminal, an ANSI color code
                          appropriate for the level of the logged record.
        %(resetcolor)s    If stderr is a terminal, an ANSI color reset code.

        """
        log_level = args.loglevel
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        log_format = self.log_format
        handler = logging.StreamHandler()  # using sys.stderr
        if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            formatter_class = self._ColorLogFormatter
        else:
            formatter_class = self._NoColorLogFormatter
        handler.setFormatter(formatter_class(log_format))
        root_logger.addHandler(handler)

        logging.info('Set log level to %s', logging.getLevelName(log_level))

    def main(self, argv):
        """Perform the tool's functions, given the specified command line
        arguments.

        This method reads the instance's config file with the
        `read_config_file()` method, adds the arguments specified in `argv`,
        and performs the subcommand identified there.

        The method returns an integer exit code suitable for using with
        `sys.exit()`. That is, `main()` returns ``0`` if the subcommand
        completes successfully, or ``1`` if the command is interrupted from the
        terminal (that is, the terminal user presses ctrl-C to raise
        `KeyboardInterrupt`). However if ``--help`` or invalid arguments are
        specified, the process is terminated by `argparse` instead and `main()`
        will not return.

        """
        config_args = self.read_config_file()
        args = config_args + argv

        parser = self.build_arg_parser()
        args = parser.parse_args(args)

        self.configure_tool(args)

        # The callable subcommand is parsed out as the "func" arg.
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
