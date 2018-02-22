# -*- coding: utf-8 -*-

from tornado import ioloop, httpserver
from traitlets import Integer, Unicode
from traitlets.config.application import Application
from .webapp import ExampleWebApp


class ExampleApp(Application):
    name = 'turret-tornado-spa-example'
    version = '0.1.0'
    description = 'Turret tornado SPA example'

    ip = Unicode('localhost', config=True, help='IP address the server will listen on.')
    port = Integer(9999, config=True, help='TCP port the server will listen on.')

    aliases = {
        "ip": "ExampleApp.ip",
        "port": "ExampleApp.port"
    }

    def initialize(self, argv=None):
        super().initialize(argv)

        self.init_webapp()

    def init_webapp(self):
        self.log.info('Starting ExampleWebApp (port: %d ip: %s)', self.port, self.ip)
        self.web_app = ExampleWebApp(log=self.log)
        self.http_server = httpserver.HTTPServer(self.web_app)
        self.http_server.listen(self.port, self.ip)

    def start(self):
        self.io_loop = ioloop.IOLoop.current()
        try:
            self.io_loop.start()
        except KeyboardInterrupt:
            self.log.info('Interrupt')

    def stop(self):
        def _stop():
            self.http_server.stop()
            self.io_loop.stop()
        self.io_loop.add_callback(_stop)


main = launch_new_instance = ExampleApp.launch_instance
