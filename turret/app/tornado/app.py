# -*- coding: utf-8 -*-

from importlib import import_module
import logging
from setuptools import find_packages
from tornado import ioloop
from unittest.mock import patch
from ..base import BaseTurretApp, capture_method_output


class TornadoApp(BaseTurretApp):
    """
    Turret app which runs a Tornado app in a kernel.

    This app runs a Tornado app in the main ioloop in which the kernel and
    other Turret apps run. To do that, this app needs to patch the ioloop
    operation at runtime.

    The Tornado app must have the following structure to be patched correctly:

    >>> class ExampleApp(Application):
    ...
    ...     def start(self):
    ...         self.io_loop = ioloop.IOLoop.current()
    ...         try:
    ...             self.io_loop.start()
    ...         except KeyboardInterrupt:
    ...             self.log.info('Interrupt')
    ...
    ...     def stop(self):
    ...         def _stop():
    ...             self.http_server.stop()
    ...             self.io_loop.stop()
    ...         self.io_loop.add_callback(_stop)

    The Tornado app
    - must call ``IOLoop.start()`` from ``start()``.
    - must call ``IOLoop.add_callback()`` from ``stop()``
        - and call ``IOLoop.stop()`` from it.
    """

    def __init__(self, app_name, turret_conf, turret_port, turret_status,
                 app_class, argv=[], uncache=None):
        """
        Initializes TurretApp.

        Parameters
        ----------
        app_name : str
            App name defined in turret.hcl.
        turret_conf : dict
            Turret conf constructed from turret.hcl.
        turret_port : int
            TCP port for Turret ZMQ channel.
        turret_status : dict
            Turret status.
        app_class : str
            Tornado application class.
        argv : list[str]
            Command line arguments for Tornado app.
        uncache : list[str]
            Module names to be uncached.
        """
        super().__init__(app_name, turret_conf, turret_port, turret_status)

        self.app_class = app_class
        self.argv = argv
        self.uncache = uncache if uncache is not None else find_packages()

    @capture_method_output
    def start(self):
        """
        Starts the Tornado app.
        """
        mod_name, cls_name = self.app_class.rsplit('.', 1)
        cls = getattr(import_module(mod_name), cls_name)
        self.app = cls()
        self.app.log = self.log

        self.log.info('Starting %s %s', type(self.app).__name__, ' '.join(self.argv))
        self.app.initialize(self.argv)

        logger = logging.getLogger('tornado')
        if logger.parent:
            logger.handlers = []  # prevent duplicated logging

        loop = ioloop.IOLoop.current()
        with patch.object(loop, 'start'):
            self.app.start()

    @capture_method_output
    def stop(self):
        """
        Stops the Tornado app.
        """
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
        """
        Restarts the tornado app.
        """
        self.uncache_modules(self.uncache)
        self.stop()
        ioloop.IOLoop.current().add_callback(self.start)

    def handle_watchdog_event(self, event):
        """
        WatchdogApp callback to be executed on filessystem update.

        Parameters
        ----------
        event : dict
            Watdhdog event.
        """
        self.log.debug('event: %s', event)
        self.restart()
