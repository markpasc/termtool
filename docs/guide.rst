==============
termtool guide
==============

`termtool` helps you write subcommand-based command line tools in Python. It collects several Python libraries into a declarative syntax:

* :mod:`argparse`, the argument parsing module with subcommand support provided in the standard library in Python 2.7 and later.
* `prettytable <http://code.google.com/p/python-progressbar/>`_, an easy module for building tables of information.
* `progressbar <http://code.google.com/p/python-progressbar/>`_, a handy module for displaying progress bars.
* :mod:`logging`, the simple built-in module for logging messages.


Making your script
==================

Each :mod:`termtool` script is defined as a :class:`~termtool.Termtool` subclass. Each subcommand in the script is an instance method marked with the :func:`~termtool.subcommand` decorator.

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

Even though decorators are evaluated closest-first, arguments are added in the order they appear in your source file (that is, in reverse order of how they evaluate). Declare positional arguments in reading order, first argument first.

Arguments that should be available in general to all commands can be specified as class decorators (in scripts for Python 2.6 and greater)::

   @argument('baz', help='the baz to frob or display')
   class Example(Termtool):

       description = 'A script that frobs or displays bazzes'

or by invoking :func:`~termtool.argument` afterward, for compatibility with Python 2.5::

   class Example(Termtool):

       description = 'A script that frobs or displays bazzes'

       ...

   argument('baz', help='the baz to frob or display')(Example)


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


Displaying tables
=================

:mod:`termtool` tools can present information to people using them in tables for easy reading. Tables can be created using the :meth:`~table()` callable on :class:`termtool.Termtool` instances.

The :meth:`~table` callable is really the :class:`prettytable.PrettyTable` class, so all arguments to the :class:`prettytable.PrettyTable` constructor are valid arguments to the :meth:`~table` callable.

::

   @subcommand(help='display the songs')
   def display(self, args):
       song = self.get_songs()

       table = self.table(['ID', 'Title', 'Artist', 'Album'])
       for song in songs:
           table.add_row([song.id, song.title, song.artist, song.album])
       print table


Displaying progress bars
========================

:mod:`termtool` tools can show people using them when they're busy performing long or multistep operations with a progress bar. Use the :meth:`~progressbar()` callable on :class:`termtool.Termtool` instances to create one.

The :meth:`~progressbar()` callable is really the :class:`progressbar.ProgressBar` class, so all arguments to the :class:`progressbar.ProgressBar` constructor are valid arguments to the :meth:`~progressbar()` callable.

::

   @subcommand(help='upload the files')
   def upload(self, args):
       files = self.get_files()

       progress = self.progressbar()
       for somefile in progress(files):
           somefile.upload()


Configuration files
===================

:mod:`termtool` tools automatically load options from "rc" style configuration files.

The tool will look for a configuration file in the user's home directory, named after the tool's class. Configuration files are simply command line elements separated each on one line. That is, each argument element that would be separated by spaces should be on a separate line; specifically, arguments that take values should be on separate lines from their values. Because configuration files are always loaded, only command-level arguments that are valid for all subcommands should be added.

For example, for a tool declared as::

   @argument('--consumer-key', help='the API consumer key')
   @argument('--consumer-secret', help='the API consumer secret')
   @argument('--access-token', help='the API access token')
   class Example(Termtool):
       ...

a configuration file specifying these API tokens would be a file named `~/.example` that contains::

   --consumer-token
   b5e53e6601cbdcc02b24
   --consumer-secret
   a8e5df863e
   --access-token
   uo9lctpryiscvujgab0cvns860xlg3

If your tool has specific arguments you may want people using it to save for later, you can use :meth:`~termtool.Termtool.write_config_file` in another command (such as `configure`) to write one out. Pass all the arguments you'd like to write out, and :class:`~termtool.Termtool` will overwrite the config file with the new settings. The file is created with umask 077 so that it's readable only by the owner.

::

   @subcommand()
   def configure(self, args):
       if not args.access_token:
           args.access_token = self.request_access_token(args)

       self.write_config_file(
           '--consumer-key', args.consumer_key,
           '--consumer-secret', args.consumer_secret,
           '--access-token', args.access_token,
       )

       logging.info("Configured!")
