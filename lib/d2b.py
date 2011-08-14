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

import sys
import os
import re
import time
from datetime import datetime

import argparse
import MySQLdb
import logging

from pygments.lexers import guess_lexer
from pygments.formatters import HtmlFormatter
from pygments import highlight

import gdata.blogger.client
import gdata.client
import gdata.sample_util
import gdata.data


class PostRenderer(object):
    _PATTERN = re.compile('(.*?)(\[code.*?\])(.*?)(\[/code\])',
                          re.DOTALL | re.MULTILINE)

    def __init__(self):
        pass

    def render(self, data):
        return re.subn('<p>\s*</p>', '',
                       '<p>' + self.__replace(data) + '</p>')[0]

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
        result = data
        result = re.subn('<!--\s*break\s*-->', '', result)[0]
        result = re.subn('\\\\r', '', result)[0]
        result = re.subn('\\\\n', '</p><p>', result)[0]
        return result

    def __replace_code(self, data):
        result = data
        result = re.subn('\\\\r', '', result)[0]
        result = re.subn('\\\\n', '\n', result)[0]
        return highlight(result, guess_lexer(result),
                           HtmlFormatter(noclasses=True,
                                         encoding='utf-8'))


class BlogEntry(object):
    _TYPE = "Generic"

    def __init__(self):
        self.title = ''
        self._body = ''
        self.nid = 0
        self.comments = []
        self.renderer = PostRenderer()
        self.published = datetime.now().isoformat()
        self.updated = self.published

    def __str__(self):
        result = self.title + '\n\n'
        result += self.__get_body() + '\n\n'
        return result

    def __get_body(self):
        return self.renderer.render(self._body)

    def __set_body(self, body):
        self._body = body

    body = property(__get_body, __set_body)


class Comment(BlogEntry):
    _TYPE = 'Comment'


class Blog(BlogEntry):
    _TYPE = 'Post'


class BlogSource(object):
    def __iter__(self):
        return self


class FileSource(BlogSource):
    _RE_POST = re.compile(r"INSERT INTO `drupal_node_revisions`" + \
                              r".*\((\d+), \d+, \d+, '(.*?)', '(.*)', " + \
                              r"'(.*?), '.*?', \d+, \d+\);")

    def __init__(self, filename):
        fd = open(filename)
        data = fd.read()
        fd.close()
        self.matcher = re.finditer(self._RE_POST, data)

    def next(self):
        match = self.matcher.next()
        if not match:
            raise StopIteration

        blog = Blog()
        blog.nid = match.group(1)
        blog.title = match.group(2)
        blog.body = match.group(3)
        return blog


class DatabaseSource(BlogSource):
    def __init__(self, user, password, database):
        self.db = MySQLdb.connect(user=user,
                                  passwd=password,
                                  db=database,
                                  charset="utf8",
                                  use_unicode=True)

        sql = "select nid,title,body,teaser,timestamp " + \
            "from drupal_node_revisions order by nid"
        self.cursor = self.db.cursor()
        self.cursor.execute(sql)

    def __del__(self):
        self.cursor.close()

    def next(self):
        item = self.cursor.fetchone()
        if not item:
            raise StopIteration
        blog = Blog()
        blog.nid = item[0]
        blog.title = item[1]
        blog.body = item[2]
        blog.comments = self.__get_comments(blog.nid)
        return blog

    def __get_comments(self, nid):
        result = []
        sql = "select comment,subject,timestamp from drupal_comments " + \
            "where nid={0} order by timestamp".format(nid)
        cursor = self.db.cursor()
        cursor.execute(sql)
        for item in cursor:
            comment = Comment()
            comment.body = item[0]
            result.append(comment)
        cursor.close()
        return result


class BlogSink(object):
    def __init__(self):
        pass

    def store(self, blog):
        raise NotImplemented("Not implemented yet")


class FileSink(BlogSink):
    def __init__(self, filepattern='d2b_post_{0:03}.txt'):
        self.pattern = filepattern

    def store(self, blog):
        filename = self.pattern.format(int(blog.nid))
        logging.getLogger().debug('Writing to file ' + filename)
        logging.getLogger().debug('\tPost: ' + blog.title)
        fd = open(filename, 'w+')
        fd.write(blog.__str__())
        fd.close()
        return True


class BloggerSink(BlogSink):
    def __init__(self, feedname=None):
        logging.getLogger().debug('Using feed: ' + str(feedname))
        self.client = gdata.blogger.client.BloggerClient()
        gdata.sample_util.authorize_client(
            self.client,
            service='blogger',
            source='Drupal2Blogger-0.0.0.1',
            scopes=['http://www.blogger.com/feeds/'])
        feeds = self.client.get_blogs()
        self.blog_id = self.__select_feed_id(feedname, feeds)
        self.previous_posts = self.__get_post_list()

    def __get_post_list(self):
        posts = self.client.get_posts(self.blog_id)
        result = []
        for each in posts.entry:
            if each.title.text:
                result.append(each.title.text)
        return result

    def __select_feed_id(self, name, feeds):
        if not name:
            return feeds[0].get_blog_id()
        for each in feeds.entry:
            if name == each.title.text:
                return each.get_blog_id()
        raise Exception('Selected feed does not exists.')

    def store(self, blog):
        if blog.title.decode('utf8') in self.previous_posts:
            logging.getLogger().warn('SKIPING post:' + blog.title)
            return
        logging.getLogger().warn('Publishing post:' + blog.title)
        self.client.add_post(self.blog_id, blog.title, blog.body)
        return True


class D2B(object):
    def __init__(self, options):
        self.options = options
        self.db = None

    def __del__(self):
        if self.db:
            self.db.close()
            self.db = None

    def run(self):
        logging.getLogger().debug('Verbose mode is ON.\n')

        source = self.__select_source()
        sink = self.__select_sink()

        n = 0
        err = 0
        for each in source:
            n += 1
            if not sink.store(each):
                err += 1
        logging.getLogger().info('{0} Posts; {1} erroneous'.format(n, err))
        return 0

    def __select_source(self):
        if self.options.parse_file:
            logging.getLogger().info('Source file: ' +
                                      self.options.parse_file)
            return FileSource(self.options.parse_file)
        logging.getLogger().info('Source database')
        return DatabaseSource(self.options.user, self.options.password,
                              self.options.database)

    def __select_sink(self):
        if self.options.use_blogger:
            logging.getLogger().info('Sink to Blogger')
            return BloggerSink(self.options.blog_title)
        logging.getLogger().info('Sink to file')
        return FileSink()


def get_blog_name():
    return time.strftime('drupalblog-%d-%M-%Y.xml')


def configure_logger(verbose):
    log = logging.getLogger()
    ch = logging.StreamHandler()
    if verbose:
        log.level = logging.DEBUG
        ch.level = logging.DEBUG
    else:
        log.level = logging.INFO
        ch.level = logging.INFO
    log.addHandler(ch)


def main():
    parser = argparse.ArgumentParser(
        description='Exports posts from Drupal to Blogger')
    parser.add_argument('-f', '--file',
                        action="store",
                        default=get_blog_name(),
                        dest='filename',
                        help='Changes the output filename by default: ' + \
                            'drupalblog_<CURRENT_DATE>.xml.')
    parser.add_argument('--parse-file',
                        action="store",
                        dest='parse_file',
                        help='Parses a SQL file instead Database.')
    parser.add_argument('-v', '--verbose',
                        action="store_true",
                        default=False,
                        dest='verbose',
                        help='Shows more information.')
    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s 2.0')

    group = parser.add_argument_group('Database Options')
    group.add_argument('-u', '--user',
                       action='store',
                       dest='user',
                       help='User to connecto to DDBB.')
    group.add_argument('-p', '--password',
                       action='store',
                       dest='password',
                       help='Password to connecto to DDBB.')
    group.add_argument('-d', '--database',
                       action='store',
                       dest='database',
                       help='Database to connect to.')

    group = parser.add_argument_group('Blogger Options')
    group.add_argument('-b', '--blogger',
                       action='store_true',
                       default=False,
                       dest='use_blogger',
                       help='Enables Blogger mode.')
    group.add_argument('-t', '--feed-title',
                       action='store',
                       dest='blog_title',
                       help='Selects the blog to save in or first one by ' + \
                           'default.')

    options = parser.parse_args()

    configure_logger(options.verbose)

    d2b = D2B(options)
    sys.exit(d2b.run())

if __name__ == '__main__':
    main()
