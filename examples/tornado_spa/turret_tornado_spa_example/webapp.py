# -*- coding: utf-8 -*-

from tornado import web
import os


class ExampleWebApp(web.Application):

    def __init__(self, log):
        self.log = log

        path = os.path.join(os.path.dirname(__file__), 'files')
        self.log.info('path: %s', path)

        super().__init__([
            (r"/(.*)", web.StaticFileHandler, {
                'path': path,
                'default_filename': 'index.html'
            })
        ])
