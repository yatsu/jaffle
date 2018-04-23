# -*- coding: utf-8 -*-

from pathlib import Path
import shlex
from tornado import gen, web
from tornado.escape import to_unicode
from tornado.httpclient import AsyncHTTPClient
from tornado.iostream import StreamClosedError
from tornado.process import Subprocess
import os


class APIExampleHandler(web.RequestHandler):
    """
    An example API handler
    """

    def initialize(self, log):
        """
        Initializes APIExampleHandler.

        Parameters
        ----------
        log : logging.Logger
            Logger.
        """
        self.log = log

    def get(self):
        """
        Handles ``GET /api/example``.
        """
        self.log.info('APIExampleHandler.get')
        self.finish({'result': 'ok'})

    def finish(self, *args, **kwargs):
        """
        Sets the ``Content-Type`` on finishing the request.
        """
        self.set_header('Content-Type', 'application/json')
        return super().finish(*args, **kwargs)


class APIStreamExampleHandler(web.RequestHandler):
    """
    An example API handler
    """

    def initialize(self, log):
        """
        Initializes APIStreamExampleHandler.

        Parameters
        ----------
        log : logging.Logger
            Logger.
        """
        self.log = log

    @gen.coroutine
    def get(self, arg):
        """
        Handles ``GET /api/stream-example``.
        """
        self.log.info('APIStreamExampleHandler.get: %s', arg)

        self.set_header('Content-Type', 'application/json')

        if arg == 'subproc':
            command = '{} -s 1 5'.format(Path(__file__).parent.parent / 'countdown')
            self.log.info('command: %s', command)
            proc = Subprocess(shlex.split(command),
                              stdout=Subprocess.STREAM, stderr=Subprocess.STREAM)
            try:
                while True:
                    line_bytes = yield proc.stdout.read_until(b'\n')
                    line = to_unicode(line_bytes).strip('\r\n')
                    self.write({'result': line})
                    self.flush()
            except StreamClosedError:
                pass
        elif arg == 'http':
            def on_recv(msg):
                line = to_unicode(msg).strip('\r\n')
                self.log.info('on_recv: %s', line)
                self.write(line)
                self.flush()

            yield AsyncHTTPClient().fetch(
                'http://localhost:9999/api/stream-example',
                streaming_callback=on_recv
            )
        else:
            for i in reversed(range(5)):
                self.log.info('countdown: %d', i)
                self.write({'result': i})
                self.flush()
                yield gen.sleep(1)

        self.finish()


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
            (r"/api/example", APIExampleHandler, {'log': self.log}),
            (r"/api/stream-example/?([^/]*)", APIStreamExampleHandler, {'log': self.log}),
            (r"/(.*)", web.StaticFileHandler, {
                'path': path,
                'default_filename': 'index.html'
            })
        ])
