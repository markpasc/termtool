#!/usr/bin/env python

import logging

from termtool import Termtool, subcommand, argument


class Example(Termtool):

    """A script that frobs or displays bazzes."""

    @subcommand()
    def loglevel(self, args):
        logging.critical('critical')
        logging.error('error')
        logging.warn('warning')
        logging.info('info')
        logging.debug('debug')

    @subcommand(help='frob a baz')
    @argument('baz', help='the baz to frob')
    def frob(self, args):
        """Do the work to frob a baz."""
        pass

    @subcommand(help='display a baz')
    @argument('baz', help='the baz to display')
    @argument('--csv', action='store_true', help='sets display mode to CSV')
    def display(self, args):
        """Display a baz."""
        pass


if __name__ == '__main__':
    Example().run()
