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
import os
import re
import codecs

import MySQLdb

from pygments.lexers import guess_lexer
from pygments.formatters import HtmlFormatter
from pygments import highlight

import gdata.blogger.client
import gdata.client
import gdata.sample_util
import gdata.data
import atom.data


class PostRenderer(object):
    _PATTERN = re.compile('(.*?)(\[code.*?\])(.*?)(\[/code\])',
                          re.DOTALL | re.MULTILINE)

    def __init__(self):
        pass

    def render(self, origin):
        return '<p>' + self.__replace(origin) + '</p>'

    def __replace(self, data):
        result = ''
        last = 0
        for each in re.finditer(self._PATTERN, data):
            result += self.__replace_text(each.group(1))
            result += self.__replace_code(each.group(3))
            last = each.end()
        result += self.__replace_text(data[last:])
        return result

    def __replace_text(self, data):
        return data.replace('\r', '').replace('\n', '</p><p>')

    def __replace_code(self, data):
        return highlight(data, guess_lexer(data),
                         HtmlFormatter(noclasses=True))


class Comment(object):
    def __init__(self):
        self._content = ''
        self.renderer = PostRenderer()

    def __get_content(self):
        return self.renderer.render(self._content)

    def __set_content(self, content):
        self._content = content

    def __str__(self):
        return self.__get_content()

    content = property(__get_content, __set_content)


class Blog(object):
    def __init__(self):
        self.title = ''
        self._body = ''
        self.nid = 0
        self.comments = []
        self.renderer = PostRenderer()

    def __str__(self):
        result = self.title + '\n\n'
        result += self.body + '\n\n'
        result += 'COMMENTS' + '\n\n'

        for each in self.comments:
            result += each.__str__() + '\n\n'
        return result

    def __get_body(self):
        return self.renderer.render(self._body)

    def __set_body(self, body):
        self._body = body

    body = property(__get_body, __set_body)


class D2B(object):
    def __init__(self, options):
        self.options = options
        self.db = None
        self.bloggerclient = None
        self.blog_id = None

    def __del__(self):
        if self.db:
            self.db.close()
            self.db = None

    def run(self):
        if self.options.verbose:
            sys.stderr.write('Verbose mode is ON.\n')

        self.__connect_to_database()
        self.__connect_to_blogger()
        self.__load_file()
        self.__get_blogs()

        return 0

    def __print(self, msg):
        if not self.options.verbose:
            return
        print msg

    def __write_to_blogger(self, blog):
        if not self.blog_id:
            return
        self.__print('Writing post: ' + blog.title)
        try:
            post_id = self.bloggerclient.add_post(self.blog_id,
                                                  blog.title,
                                                  blog.body, draft=False)
            for each in blog.comments:
                self.__print('Writing comment: ')
                self.bloggerclient.add_comment(self.blog_id, post_id,
                                               each.content)
        except gdata.client.RequestError as e:
            print e

    def __write_to_hd(self, blog):
        if not self.options.save_to_file:
            return

        fd = codecs.open("d2b_post_{0}.txt".format(blog.nid), 'w+', 'utf-8')
        #fd = open("d2b_post_{0}.txt".format(blog.nid), 'w+')
        fd.write(blog.__str__())
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
            blog.title = item[1]  # .decode('utf-8').encode('utf-8')
            blog.body = item[2]
            blog.comments = self.__get_comments(blog.nid)
            self.__write_to_hd(blog)
            self.__write_to_blogger(blog)
        cursor.close()
        self.db.commit()

    def __get_comments(self, nid):
        result = []
        sql = "select comment from drupal_comments " + \
            "where nid={0} order by timestamp".format(nid)
        cursor = self.db.cursor()
        cursor.execute(sql)
        for item in cursor:
            comment = Comment()
            comment.content = item[0]  # .decode('utf-8').encode('utf-8')
            result.append(comment)
        cursor.close()
        return result

    def __load_file(self):
        if not self.options.file:
            return

        self.__assert_file_exists()

        for each in self.__read_file().split('\n\n'):
            query = each.strip()
            if query:
                self.__execute_script(query)

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

    def __connect_to_blogger(self):
        if not self.options.send_to_blogger:
            return
        if not self.options.blog_name:
            print 'Cannot send to bogger. Please, specify a Blog Name.'
            return
        self.bloggerclient = gdata.blogger.client.BloggerClient()
        gdata.sample_util.authorize_client(
            self.bloggerclient,
            service='blogger',
            source='Drupal2Blogger-0.0.0.1',
            scopes=['http://www.blogger.com/feeds/'])
        feed = self.bloggerclient.get_blogs()
        for each in feed.entry:
            if self.options.blog_name == each.title.text:
                self.blog_id = each.get_blog_id()
                break

    def __connect_to_database(self):
        if not self.options.user or \
                not self.options.password or \
                not self.options.database:
            return

        self.db = MySQLdb.connect(user=self.options.user,
                                  passwd=self.options.password,
                                  db=self.options.database,
                                  charset="utf8")


def main():
    parser = OptionParser()
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

    group = OptionGroup(parser, 'Blogger Options',
                        'Options to use with Blogger.')
    group.add_option('--send-to-blogger', action='store_true', default=False,
                    dest='send_to_blogger',
                    help='Will send data to Blogger.')
    group.add_option('--blog-name', action='store',
                    dest='blog_name',
                    help='Name of the blog to use.')
    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    d2b = D2B(options)
    sys.exit(d2b.run())

if __name__ == '__main__':
    main()
