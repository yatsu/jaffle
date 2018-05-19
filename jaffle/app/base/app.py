# -*- coding: utf-8 -*-

import logging
import shlex
import sys
from tornado import gen
from tornado.escape import to_unicode
from tornado.iostream import StreamClosedError
from tornado.process import Subprocess
from ...config import ConfigDict
from ...job import Job
from ...utils import str_value
from .config import AppConfig
from .logging import JaffleAppLogHandler


class BaseJaffleApp(object):
    """
    Base class for Jaffle apps.
    """

    completer_class = None
    lexer_class = None
    app_conf = None
    jobs = None

    def __init__(self, app_conf_data):
        """
        Initializes BaseJaffleApp.

        Parameters
        ----------
        app_conf_data : dict
            App configuration data.
        """
        self.app_conf = AppConfig.from_dict(app_conf_data)
        self.ipython = get_ipython()  # noqa

        logging.getLogger().handlers = []

        self.log = logging.getLogger(self.app_name)
        level = str_value(self.conf.get('logger', {}).get('level', 'info'))
        self.log.setLevel(getattr(logging, level.upper()))
        self.log.handlers = [JaffleAppLogHandler(self.app_name, self.jaffle_port)]
        self.log.propagate = False

        self.jobs = {}
        for job_name, job_data in self.jobs_conf.items():
            logger = logging.getLogger(job_name)
            logger.parent = self.log
            logger.setLevel(self.log.level)
            self.jobs[job_name] = Job(logger, job_name, job_data.get('command'))

    @property
    def app_name(self):
        """
        Returns the app name.

        Returns
        -------
        app_name : str
            App name.
        """
        return self.app_conf.app_name

    @property
    def conf(self):
        """
        Returns the app-specific config.

        Returns
        -------
        conf : ConfigDict
            App-specific config.
        """
        return self.app_conf.conf

    @property
    def options(self):
        """
        Retruns options for the app.

        Returns
        -------
        options : dict
            Options for the app.
        """
        return self.app_conf.conf.get('options', ConfigDict())

    @property
    def raw_namespace(self):
        """
        Returns the raw namespace for string interpolation which does not
        include functions and variables.

        Returns
        -------
        raw_namespace : dict
            Raw namespace for string interpolation.
        """
        return self.app_conf.raw_namespace

    @property
    def runtime_variables(self):
        """
        Returns runtime variables.

        Returns
        -------
        runtime_variables : dict
            Runtime variables.
        """
        return self.app_conf.runtime_variables

    @property
    def jaffle_port(self):
        """
        Returns the Jaffle port.

        Returns
        -------
        jaffle_port : int
            Jaffle port.
        """
        return self.app_conf.jaffle_port

    @property
    def jobs_conf(self):
        """
        Returns jobs config.

        Returns
        -------
        jobs_conf : ConfigDict
            Jobs config.
        """
        return self.app_conf.jobs_conf

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

    def clear_module_cache(self, modules):
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

        self.log.debug('clearing module cache: %s', modules)
        for mod in [mod for mod in sys.modules if match(mod)]:
            self.log.debug('  clear: %s', mod)
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
