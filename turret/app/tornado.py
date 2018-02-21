# -*- coding: utf-8 -*-

from importlib import import_module
import sys
from tornado import ioloop
from unittest.mock import patch
from .base import BaseTurretApp, capture_method_output


class TornadoApp(BaseTurretApp):

    def __init__(self, app_name, turret_conf, turret_port, sessions,
                 app_cls, argv=[], uncache_modules=[]):
        super().__init__(app_name, turret_conf, turret_port, sessions)

        self.app_cls = app_cls
        self.argv = argv
        self.uncache_modules = uncache_modules

    @capture_method_output
    def start(self):
        self.uncache()

        mod_name, cls_name = self.app_cls.rsplit('.', 1)
        cls = getattr(import_module(mod_name), cls_name)
        self.app = cls()
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
        self.stop()
        ioloop.IOLoop.current().add_callback(self.start)

    def uncache(self):
        def match(mod):
            return any([mod == m or mod.startswith('{}.'.format(m)) for m in self.uncache_modules])

        for mod in [mod for mod in sys.modules if match(mod)]:
            self.log.debug('uncache: %s', mod)
            del sys.modules[mod]

    def handle_watchdog_event(self, event):
        self.log.debug('event: %s', event)
        self.restart()
