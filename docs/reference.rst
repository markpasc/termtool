========================
`termtool` API Reference
========================

.. module:: termtool

.. function:: subcommand([help,] **kwargs)

   A decorator (that is, *returns* a decorator) to mark a function as a :class:`Termtool` subcommand. Arguments are passed to the :class:`argparse.ArgumentParser` constructor, so any of its arguments are valid keyword arguments.

.. function:: argument(name or flags...[, help], **kwargs)

   A decorator (that is, *returns* a decorator) to declare an argument of a subcommand method or command class. Arguments are passed to the :meth:`argparse.ArgumentParser.add_argument` method of the command's :class:`argparse.ArgumentParser` instance, so any of its arguments are valid.

.. class:: Termtool()

   Creates a new :class:`Termtool` instance. Make your own command line tool by subclassing this class and defining new subcommands with the :func:`subcommand` decorator.

   .. method:: table([field_names,] **kwargs)

      Returns a new :class:`prettytable.PrettyTable` instance.

      Any arguments for the :class:`prettytable.PrettyTable` constructor are valid arguments to :meth:`table`. See `the prettytable documentation <http://code.google.com/p/prettytable/>`_ for more information.

   .. method:: progressbar([max_val,] **kwargs)

      Returns a new :class:`progressbar.ProgressBar` instance.

      Any arguments for the :class:`progressbar.ProgressBar` constructor are valid arguments to :meth:`progressbar`. See `the progressbar documentation <http://code.google.com/p/python-progressbar/>`_ for more information.

   .. method:: read_config_file()

      Reads any additional arguments saved in the user's configuration file for the tool and returns them as a list.

      Configuration files are files in the user's home directory named `.toolname` where `toolname` is the name of the tool class in lower case. The file if present should contain arguments one per line.

   .. method:: write_config_file(config_args)

      Replaces the user's configuration file with the arguments present in `config_args`.

      This method will overwrite any unexpected changes the user has made to the configuration file, so only use it in response to an explicit instruction by the user, such as in a ``configure`` command. If the file is created, it is created with umask 077 so that it is neither group nor world readable.

   .. method:: main(argv)

      Invokes the tool with the specified command line arguments, returning the appropriate exit code.

      :meth:`main` first reads the "rc" style configuration file, prepending its arguments to `argv` before the other arguments. The arguments are then parsed and the :mod:`logging` module is first configured. :meth:`main` then dispatches to the instance method matching the subcommand specified by the first positional argument in `argv`.

   .. method:: run()

      Invokes the tool as run from a script.

      Command line arguments are read from :data:`python:sys.argv`. When the tool's run is complete, :meth:`run` exits the interpreter using :func:`python:sys.exit` with an appropriate exit code (`0` if the run completed normally and a non-zero value otherwise) when complete.

      Use this method in your ``if __name__ == '__main__'`` block.
