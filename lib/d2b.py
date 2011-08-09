#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

# Drupal2Blogger
#
# Copyright (C) 2011 Miguel Angel Garcia <miguelangel.garcia@gmail.com>
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from optparse import OptionParser
from optparse import OptionGroup
import sys


class D2B(object):
    def __init__(self, options):
        self.options = options

    def run(self):
        if self.options.verbose:
            sys.stderr.write('Verbose mode is ON.\n')
        if self.options.file:
            sys.stderr.write('The file do not exists.\n')
            return 2
        return 0


def main():
    parser = OptionParser()
    parser.add_option("--no-blogger", action="store_false", default=True,
                      dest="blogger",
                      help="Do not use blogger to save documents.")
    parser.add_option('-v', '--verbose', action="store_true", default=False,
                      dest='verbose',
                      help='Shows more information.')

    group = OptionGroup(parser, 'Database Options',
                        'Options to use with Database.')
    group.add_option('-f', "--file", action="store",
                      dest='file',
                      help='File to load database.')
    group.add_option('-u', '--user', action='store',
                    dest='user',
                    help='User to connecto to DDBB.')
    group.add_option('-p', '--password', action='store',
                    dest='password',
                    help='Password to connecto to DDBB.')
    group.add_option('-d', '--database', action='store',
                    dest='database',
                    help='Database to connect to.')

    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    d2b = D2B(options)
    sys.exit(d2b.run())

if __name__ == '__main__':
    main()
