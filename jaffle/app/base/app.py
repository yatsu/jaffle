# -*- coding: utf-8 -*-

from functools import wraps
import logging
import shlex
import sys
import threading
from tornado import gen, ioloop
from tornado.escape import to_unicode
from tornado.iostream import StreamClosedError
from tornado.process import Subprocess
from unittest.mock import patch
import zmq
from zmq.eventloop import zmqstream
from ...job import Job
from ...status import JaffleStatus
from .logging import JaffleAppLogHandler


class BaseJaffleApp(object):
    """
    Base class for Jaffle apps.
    """

    completer_class = None
    lexer_class = None
    jobs = None

    def __init__(self, app_name, jaffle_conf, jaffle_port, jaffle_status):
        """
        Initializes BaseJaffleApp.

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
        """
        self.app_name = app_name
        self.jaffle_port = jaffle_port
        self.jaffle_conf = jaffle_conf
        self.jaffle_status = JaffleStatus.from_dict(jaffle_status)
        self.ipython = get_ipython()  # noqa

        logging.getLogger().handlers = []

        self.log = logging.getLogger(app_name)
        level = jaffle_conf.get('app', {})[app_name].get('logger', {}).get('level', 'info')
        self.log.setLevel(getattr(logging, level.upper()))
        self.log.handlers = [JaffleAppLogHandler(app_name, self.jaffle_stream)]
        self.log.propagate = False

        self.jobs = {}
        for job_name, job_data in jaffle_conf.get('job', {}).items():
            logger = logging.getLogger(job_name)
            logger.parent = self.log
            logger.setLevel(self.log.level)
            self.jobs[job_name] = Job(logger, job_name, job_data.get('command'))

        self._jaffle_streams = {}

    def execute_code(self, code, *args, **kwargs):
        """
        Executes a code.

        Parameters
        ----------
        code : str
            Code to be executed.
            It will be formateed as ``code.format(*args, **kwargs)``.
        args : list
            Positional arguments to ``code.format()``.
        kwargs : dict
            Keyward arguments to ``code.formmat()``.

        Returns
        -------
        future : tornado.gen.Future
            Future which will have the execution result.
        """
        future = gen.Future()
        result = self.ipython.run_cell(code.format(*args, **kwargs))
        future.set_result(result.result)
        return future

    @gen.coroutine
    def execute_command(self, command, logger=None):
        """
        Executes a command.

        Parameters
        ----------
        command : str
            Command to be executed.
        logger : logging.Logger
            Logger.

        Returns
        -------
        future : tornado.gen.Future
            Future which will have the execution result.
        """
        log = logger or self.log
        log.debug('Executing command: %s', command)
        proc = Subprocess(shlex.split(command), stdout=Subprocess.STREAM, stderr=Subprocess.STREAM)
        try:
            while True:
                line_bytes = yield proc.stdout.read_until(b'\n')
                line = to_unicode(line_bytes).strip('\r\n')
                log.info(line)
        except StreamClosedError:
            pass

    @gen.coroutine
    def execute_job(self, job_name):
        """
        Executes a job.

        Parameters
        ----------
        job_name : str
            Job to be executed.

        Returns
        -------
        future : tornado.gen.Future
            Future which will have the execution result.
        """
        job = self.jobs[job_name]
        result = yield self.execute_command(job.command, logger=job.log)
        return result

    def invalidate_module_cache(self, modules):
        """
        Clears the module cache.

        This method deletes cache of imported modules from ``sys.modules``
        whose name starts with specified modules.
        For example, ``jaffle`` is specified, ``jaffle.app`` will also be
        deleted.

        Parameters
        ----------
        modules : str[list]
            List of module (dot separated module names).
        """
        def match(mod):
            return any([mod == m or mod.startswith('{}.'.format(m)) for m in modules])

        self.log.debug('invalidating module cache: %s', modules)
        for mod in [mod for mod in sys.modules if match(mod)]:
            self.log.debug('  invalidate %s', mod)
            del sys.modules[mod]

    @classmethod
    def command_to_code(self, app_name, command):
        """
        Converts a command comes from ``jaffle attach <app>`` to a code to be
        executed.

        If the app supports ``jaffle attach``, this method must be implemented.

        Parameters
        ----------
        app_name : str
            App name defined in jaffle.hcl.
        command : str
            Command name received from the shell of ``jaffle attach``.

        Returns
        -------
        code : str
            Code to be executed.
        """
        raise NotImplementedError('Must be implemented to support attaching')

    def jaffle_stream(self):
        """
        Returns the Jaffle ZeroMQ stream for the current thread.
        Each thread must have its own ZeroMQ stream.

        Returns
        -------
        stream : zmq.eventloop.zmqstream.ZMQStream
            Jaffle ZeroMQ stream for the current thread.
        """
        current_thread_id = threading.current_thread().ident

        if current_thread_id in self._jaffle_streams:
            return self._jaffle_streams[current_thread_id]

        ctx = zmq.Context.instance()
        socket = ctx.socket(zmq.PUSH)
        socket.connect('tcp://127.0.0.1:{0}'.format(self.jaffle_port))
        stream = self._jaffle_streams[current_thread_id] = (
            zmqstream.ZMQStream(socket, ioloop.IOLoop.current())
        )
        return stream


def invalidate_module_cache_once(method):
    """
    Decorator for an app method to ensure doing invalidate only once.
    You can call ``BaseJaffleApp.invalidate_module_cache()`` multiple times without
    worrying duplicated invalidation.

    Parameters
    ----------
    method : function
        Method to be wrapped.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        invalidated = False
        __invalidate_module_cache = self.invalidate_module_cache

        def _invalidate_module_cache(modules):
            nonlocal invalidated
            if invalidated:
                return
            __invalidate_module_cache(modules)
            invalidated = True

        with patch.object(self, 'invalidate_module_cache', _invalidate_module_cache):
            return method(self, *args, **kwargs)

    return wrapper