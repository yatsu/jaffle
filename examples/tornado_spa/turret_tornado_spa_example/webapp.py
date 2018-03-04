# -*- coding: utf-8 -*-

from tornado import web
import os


class APIHandler(web.RequestHandler):
    """
    An example API handler
    """

    def initialize(self, log):
        """
        Initializes APIHandler.

        Parameters
        ----------
        log : logging.Logger
            Logger.
        """
        self.log = log

    def get(self):
        """
        Handles ``GET /api``.
        """
        self.log.info('APIHandler.get')
        self.finish({'result': 'ok'})

    def finish(self, *args, **kwargs):
        """
        Sets the ``Content-Type`` on finishing the request.
        """
        self.set_header('Content-Type', 'application/json')
        return super().finish(*args, **kwargs)


class ExampleWebApp(web.Application):
    """
    An Example Tornado web app.
    """

    def __init__(self, log):
        """
        Initializes ExampleWebApp.

        Parameters
        ----------
        log : logging.Logger
            Logger.
        """
        self.log = log

        path = os.path.join(os.path.dirname(__file__), 'files')

        super().__init__([
            (r"/api", APIHandler, {'log': self.log}),
            (r"/(.*)", web.StaticFileHandler, {
                'path': path,
                'default_filename': 'index.html'
            })
        ])
