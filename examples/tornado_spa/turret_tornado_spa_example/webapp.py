# -*- coding: utf-8 -*-

from tornado import web
import os


class APIHandler(web.RequestHandler):

    def initialize(self, log):
        self.log = log

    def get(self):
        self.log.info('APIHandler.get')
        self.finish({'result': 'ok'})

    def finish(self, *args, **kwargs):
        self.set_header('Content-Type', 'application/json')
        return super().finish(*args, **kwargs)


class ExampleWebApp(web.Application):

    def __init__(self, log):
        self.log = log

        path = os.path.join(os.path.dirname(__file__), 'files')
        self.log.info('path: %s', path)

        super().__init__([
            (r"/api", APIHandler, {'log': self.log}),
            (r"/(.*)", web.StaticFileHandler, {
                'path': path,
                'default_filename': 'index.html'
            })
        ])
