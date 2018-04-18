# -*- coding: utf-8 -*-

from functools import wraps
import logging
import shlex
import sys
from tornado import gen
from tornado.escape import to_unicode
from tornado.iostream import StreamClosedError
from tornado.process import Subprocess
from unittest.mock import patch
import zmq
from ...job import Job
from ...status import TurretStatus
from .logging import TurretAppLogHandler


class BaseTurretApp(object):
    """
    Base class for Turret apps.
    """

    completer_class = None
    lexer_class = None
    jobs = None

    def __init__(self, app_name, turret_conf, turret_port, turret_status):
        """
        Initializes BaseTurretApp.

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
        """
        self.app_name = app_name
        self.turret_port = turret_port
        self.turret_conf = turret_conf
        self.turret_status = TurretStatus.from_dict(turret_status)
        self.ipython = get_ipython()  # noqa

        ctx = zmq.Context.instance()
        self.turret_socket = ctx.socket(zmq.PUSH)
        self.turret_socket.connect('tcp://127.0.0.1:{0}'.format(self.turret_port))

        self.log = logging.getLogger(app_name)
        level = turret_conf.get('app', {})[app_name].get('logger', {}).get('level', 'info')
        self.log.setLevel(getattr(logging, level.upper()))
        handler = TurretAppLogHandler(app_name, self.turret_socket)
        self.log.addHandler(handler)

        self.jobs = {}
        for job_name, job_data in turret_conf.get('job', {}).items():
            logger = logging.getLogger(job_name)
            logger.parent = self.log
            logger.setLevel(self.log.level)
            self.jobs[job_name] = Job(logger, job_name, job_data.get('command'))

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

    def invalidate_modules(self, modules):
        """
        Clears the module cache.

        This method deletes cache of imported modules from ``sys.modules``
        whose name starts with specified modules.
        For example, ``turret`` is specified, ``turret.app`` will also be
        deleted.

        Parameters
        ----------
        modules : str[list]
            List of module (dot separated module names).
        """
        def match(mod):
            return any([mod == m or mod.startswith('{}.'.format(m)) for m in modules])

        for mod in [mod for mod in sys.modules if match(mod)]:
            self.log.debug('invalidate: %s', mod)
            del sys.modules[mod]

    @classmethod
    def command_to_code(self, app_name, command):
        """
        Converts a command comes from ``turret attach <app>`` to a code to be
        executed.

        If the app supports ``turret attach``, this method must be implemented.

        Parameters
        ----------
        app_name : str
            App name defined in turret.hcl.
        command : str
            Command name received from the shell of ``turret attach``.

        Returns
        -------
        code : str
            Code to be executed.
        """
        raise NotImplementedError('Must be implemented to support attaching')


def invalidate_modules_once(method):
    """
    Decorator for an app method to ensure doing invalidate only once.
    You can call ``BaseTurretApp.invalidate_modules()`` multiple times without
    worrying duplicated invalidation.

    Parameters
    ----------
    method : function
        Method to be wrapped.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        invalidated = False
        __invalidate_modules = self.invalidate_modules

        def _invalidate_modules(modules):
            nonlocal invalidated
            if invalidated:
                return
            __invalidate_modules(modules)
            invalidated = True

        with patch.object(self, 'invalidate_modules', _invalidate_modules):
            return method(self, *args, **kwargs)

    return wrapper
