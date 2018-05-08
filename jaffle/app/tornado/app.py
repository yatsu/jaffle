# -*- coding: utf-8 -*-

from distutils.version import StrictVersion
from importlib import import_module
import jupyter_client
from jupyter_client.threaded import IOLoopThread
import logging
from setuptools import find_packages
from tornado import ioloop
from unittest.mock import patch
from ..base import BaseJaffleApp, capture_method_output


class TornadoBridgeApp(BaseJaffleApp):
    """
    Jaffle app which runs a Tornado app in a kernel.

    This app runs a Tornado app in the main ioloop in which the kernel and
    other Jaffle apps run. To do that, this app needs to patch the ioloop
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

    def __init__(self, app_name, jaffle_conf, jaffle_port, jaffle_status,
                 app_class, args=[], clear_cache=None, threaded=False):
        """
        Initializes JaffleApp.

        Parameters
        ----------
        app_name : str
            App name defined in jaffle.hcl.
        jaffle_conf : dict
            Jaffle conf constructed from jaffle.hcl.
        jaffle_port : int
            TCP port for Jaffle ZMQ channel.
        jaffle_status : dict
            Jaffle status.
        app_class : str
            Tornado application class.
        args : list[str]
            Command line arguments for Tornado app.
        clear_cache : list[str] or None
            Module names to be cleared from cache.
        threaded : bool
            Whether to launch the app in an independent thread.
        """
        super().__init__(app_name, jaffle_conf, jaffle_port, jaffle_status)

        self.app_class = app_class
        self.args = args
        self.clear_cache = (clear_cache if clear_cache is not None else find_packages())
        self.threaded = threaded
        self.thread = None
        self.main_io_loop = None

    @capture_method_output
    def start(self):
        """
        Starts the Tornado app.
        """
        mod_name, cls_name = self.app_class.rsplit('.', 1)
        cls = getattr(import_module(mod_name), cls_name)
        self.app = cls()
        self.app.log = self.log

        self.app.initialize(self.args)

        from tornado.log import app_log, access_log, gen_log
        for log in app_log, access_log, gen_log:
            log.name = self.log.name

        logger = logging.getLogger('tornado')
        if logger.parent:
            logger.handlers = []  # prevent duplicated logging
        logger.propagate = True
        logger.parent = self.log
        logger.setLevel(self.log.level)

        self.main_io_loop = ioloop.IOLoop.current()
        if self.threaded:
            io_loop = ioloop.IOLoop()
            if StrictVersion(jupyter_client.__version__) < StrictVersion('5.2.3'):
                self.thread = IOLoopThread(io_loop)
            else:
                self.thread = IOLoopThread()
            self.log.info('Starting %s %s %s',
                          type(self.app).__name__, ' '.join(self.args), self.thread)
            io_loop.make_current()
            with patch.object(io_loop, 'start'):
                self.app.start()
            self.main_io_loop.make_current()
            with patch('jupyter_client.threaded.ioloop.IOLoop', return_value=io_loop):
                self.thread.start()
        else:
            self.log.info('Starting %s %s', type(self.app).__name__, ' '.join(self.args))
            with patch.object(self.main_io_loop, 'start'):
                self.app.start()

    @capture_method_output
    def stop(self, stop_callback=None):
        """
        Stops the Tornado app.

        Parameters
        ----------
        stop_callback : function
            Callback to be called after ``app.stop()``.
        """
        self.log.info('Stopping %s', type(self.app).__name__)

        if self.threaded:
            app_io_loop = self.thread.ioloop
        else:
            app_io_loop = self.main_io_loop

        add_callback_org = app_io_loop.add_callback

        def add_callback(callback_org):
            def new_callback():
                with patch.object(app_io_loop, 'stop'):
                    callback_org()
                    self.app = None

                    if self.threaded:
                        def stop_thread():
                            self.thread.stop()
                            self.thread = None
                            if stop_callback():
                                stop_callback()

                        self.main_io_loop.add_callback(stop_thread)
                    else:
                        if stop_callback():
                            stop_callback()

            add_callback_org(new_callback)

        with patch.object(app_io_loop, 'add_callback', add_callback):
            self.app.stop()

    def restart(self):
        """
        Restarts the tornado app.
        """
        def stop_callback():
            self.clear_module_cache(self.clear_cache)
            self.start()

        self.stop(stop_callback)

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
