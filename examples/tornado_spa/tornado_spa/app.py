# -*- coding: utf-8 -*-

from tornado import ioloop, httpserver
from traitlets import Integer, Unicode
from traitlets.config.application import Application
from .webapp import ExampleWebApp


class ExampleApp(Application):
    """
    Example Tornado application.
    This class handles command-line and main ioloop.
    """
    name = 'jaffle-tornado-spa-example'
    version = '0.1.0'
    description = 'Jaffle tornado SPA example'

    ip = Unicode('localhost', config=True, help='IP address the server will listen on.')
    port = Integer(9999, config=True, help='TCP port the server will listen on.')

    aliases = {
        "ip": "ExampleApp.ip",
        "port": "ExampleApp.port"
    }

    def initialize(self, argv=None):
        """
        Initializes ExampleApp.

        Parameters
        ----------
        argv : list[str]
            Command line strings.
        """
        super().initialize(argv)

    def init_webapp(self):
        """
        Initializes the web app (ExampleWebApp).
        """
        self.log.info('Starting ExampleWebApp (port: %d ip: %s)', self.port, self.ip)
        self.web_app = ExampleWebApp(log=self.log)
        self.http_server = httpserver.HTTPServer(self.web_app)
        self.http_server.listen(self.port, self.ip)

    def start(self):
        """
        Starts the main ioloop.
        """
        self.io_loop = ioloop.IOLoop.current()

        self.init_webapp()

        try:
            self.io_loop.start()
        except KeyboardInterrupt:
            self.log.info('Interrupt')

    def stop(self):
        """
        Stops the main ioloop.
        """
        def _stop():
            self.http_server.stop()
            self.io_loop.stop()
        self.io_loop.add_callback(_stop)


main = launch_new_instance = ExampleApp.launch_instance
