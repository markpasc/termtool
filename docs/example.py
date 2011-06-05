#!/usr/bin/env python

import logging

from termtool import Termtool, subcommand, argument


class Example(Termtool):

    description = 'A script that frobs or displays bazzes'

    @subcommand()
    def loglevel(self, args):
        logging.critical('critical')
        logging.error('error')
        logging.warn('warning')
        logging.info('info')
        logging.debug('debug')

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
