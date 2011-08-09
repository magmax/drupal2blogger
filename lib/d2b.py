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
import MySQLdb
import sys
import os


class Blog(object):
    def __init__(self):
        self.title = ''
        self.body = ''
        self.nid = 0

    def __str__(self):
        return self.title + '\n\n' + self.body


class D2B(object):
    def __init__(self, options):
        self.options = options
        self.db = None
        self.blogs = []

    def __del__(self):
        if self.db:
            self.db.close()
            self.db = None

    def run(self):
        if self.options.verbose:
            sys.stderr.write('Verbose mode is ON.\n')

        self.__connect_to_database()
        self.__load_file()
        self.__get_blogs()
        self.__write_to_hd()

        return 0

    def __write_to_hd(self):
        if not self.options.save_to_file:
            return

        for item in self.blogs:
            fd = open("d2b_post_{0}.txt".format(item.nid), 'w+')
            fd.write(str(item))
            fd.close()

    def __get_blogs(self):
        if not self.db:
            return

        sql = "select nid,title,body from drupal_node_revisions order by nid"
        cursor = self.db.cursor()
        cursor.execute(sql)
        for item in cursor:
            blog = Blog()
            blog.nid = item[0]
            blog.title = item[1]
            blog.body = item[2]
            self.blogs.append(blog)
        cursor.close()
        self.db.commit()

    def __load_file(self):
        if not self.options.file:
            return

        self.__assert_file_exists()

        self.__execute_script(self.__read_file())

    def __execute_script(self, script):
        cursor = self.db.cursor()
        cursor.execute(script)
        cursor.close()
        self.db.commit()

    def __read_file(self):
        fd = open(self.options.file)
        result = fd.read()
        fd.close()
        return result

    def __assert_file_exists(self):
        if not os.path.exists(self.options.file):
            sys.stderr.write('The file do not exists.\n')
            sys.exit(2)

    def __connect_to_database(self):
        if not self.options.user or \
                not self.options.password or \
                not self.options.database:
            return

        self.db = MySQLdb.connect(user=self.options.user,
                                  passwd=self.options.password,
                                  db=self.options.database)


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
    group.add_option('--save-to-file', action='store_true', default=False,
                    dest='save_to_file',
                    help='Database to connect to.')

    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    d2b = D2B(options)
    sys.exit(d2b.run())

if __name__ == '__main__':
    main()
