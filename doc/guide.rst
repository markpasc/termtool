==============
termtool guide
==============

`termtool` helps you write subcommand-based command line tools in Python. It collects several Python libraries into a declarative syntax:

* :mod:`argparse`, the argument parsing module with subcommand support provided in the standard library in Python 2.7 and later.
* `prettytable`, an easy module for building tables of information.
* `progressbar`, a handy module for displaying progress bars.
* :mod:`logging`, the simple built-in module for logging messages.


Making your script
==================

Each `termtool` script is defined as a :class:`Termtool` subclass. Each subcommand in the script is an instance method marked with the :func:`subcommand` decorator.

A script like this::

    #!/usr/bin/env python

    from termtool import Termtool, subcommand, argument


    class Example(Termtool):

        description = 'A script that frobs or displays bazzes'

        @subcommand(help='frobs a baz')
        @argument('baz', help='the baz to frob')
        def frob(self, args):
            # do the work to frob a baz
            pass

        @subcommand(help='displays a baz')
        @argument('baz', help='the baz to display')
        @argument('--csv', action='store_true', help='sets display mode to CSV')
        def display(self, args):
            # display the baz
            pass


    if __name__ == '__main__':
        Example().run()

creates a command like this::

    $ example --help
    usage: example [-h] [-v] [-q] COMMAND ...

    A script that frobs or displays bazzes

    optional arguments:
      -h, --help  show this help message and exit
      -v          be more verbose (stackable)
      -q          be less verbose (stackable)

    subcommands:
      COMMAND
        frob      frobs a baz
        display   displays a baz

    $ example display --help
    usage: example.py display [-h] [--csv] baz

    positional arguments:
      baz         the baz to display

    optional arguments:
      -h, --help  show this help message and exit
      --csv       sets display mode to CSV

    $


The arguments to the :func:`termtool.subcommand` decorator describe the subcommand itself. Subcommands are created using `argparse subcommands <http://python.readthedocs.org/en/latest/library/argparse.html#sub-commands>`_, so any argument you can pass to the :class:`ArgumentParser <argparse.ArgumentParser>` constructor is valid for :func:`~termtool.subcommand`.

Arguments themselves are declared with the :func:`termtool.argument` decorator. Subcommand arguments are declared with :meth:`ArgumentParser.add_argument <argparse.ArgumentParser.add_argument>`, so all its arguments are valid for the :func:`~termtool.argument` decorator.


Logging
=======

:mod:`termtool` tools provide automatic support for configuring the :mod:`logging` module. Log messages are formatted simply with the level and the message, and are printed to standard error.

People using your tool can use the `-v` and `-q` arguments to change the log level. By default, messages at `WARN` and lower logging levels are displayed. Each `-v` argument adds one more verbose level of logging, and each `-q` argument removes one level, down to `CRITICAL` level. Critical errors are always displayed.

For example, given the command::

   @subcommand()
   def loglevel(self, args):
       logging.critical('critical')
       logging.error('error')
       logging.warn('warning')
       logging.info('info')
       logging.debug('debug')

you would see output such as::

   $ example loglevel
   CRITICAL: critical
   ERROR: error
   WARNING: warning

   $ example -v -v loglevel
   INFO: Set log level to DEBUG
   CRITICAL: critical
   ERROR: error
   WARNING: warning
   INFO: info
   DEBUG: debug

   $ example -q -q loglevel
   CRITICAL: critical

   $ example -qqqqq loglevel
   CRITICAL: critical

   $ example -qqqqqvvvvvqvqvqqv loglevel
   CRITICAL: critical
   ERROR: error

