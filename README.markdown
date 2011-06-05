# termtool #

`termtool` is a module for declaratively making command line tools in Python. It uses:

* `argparse`
* [`PrettyTable`](http://pypi.python.org/pypi/PrettyTable)
* [`ProgressBar`](http://pypi.python.org/pypi/progressbar)


## Installation ##

Install it as any other Python program:

    $ python setup.py install

If you don't want to install its dependencies system-wide, try installing it in a [virtual environment](http://www.virtualenv.org/).


## Usage ##

See `bin/rdio`, a converted version of [`rdio-cli`][rdio-cli], for an example script.

[rdio-cli]: https://github.com/markpasc/rdio-cli
