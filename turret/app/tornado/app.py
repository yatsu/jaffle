# -*- coding: utf-8 -*-

from importlib import import_module
from setuptools import find_packages
from tornado import ioloop
from unittest.mock import patch
from ..base import BaseTurretApp, capture_method_output


class TornadoApp(BaseTurretApp):

    def __init__(self, app_name, turret_conf, turret_port, turret_status,
                 app_cls, argv=[], uncache=[]):
        super().__init__(app_name, turret_conf, turret_port, turret_status)

        self.app_cls = app_cls
        self.argv = argv
        self.uncache = uncache or find_packages()

    @capture_method_output
    def start(self):
        mod_name, cls_name = self.app_cls.rsplit('.', 1)
        cls = getattr(import_module(mod_name), cls_name)
        self.app = cls()
        self.app.log = self.log

        self.log.info('Starting %s %s', type(self.app).__name__, ' '.join(self.argv))
        self.app.initialize(self.argv)

        loop = ioloop.IOLoop.current()
        with patch.object(loop, 'start'):
            self.app.start()

    @capture_method_output
    def stop(self):
        self.log.info('Stopping %s', type(self.app).__name__)
        loop = ioloop.IOLoop.current()
        __add_callback = loop.add_callback

        def _add_callback(callback):
            def new_callback():
                with patch.object(loop, 'stop'):
                    callback()

            __add_callback(new_callback)

        with patch.object(loop, 'add_callback', _add_callback):
            self.app.stop()

    def restart(self):
        self.uncache_modules(self.uncache)
        self.stop()
        ioloop.IOLoop.current().add_callback(self.start)

    def handle_watchdog_event(self, event):
        self.log.debug('event: %s', event)
        self.restart()
