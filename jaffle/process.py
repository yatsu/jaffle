# -*- coding: utf-8 -*-

import os
import re
import shlex
import signal
from subprocess import TimeoutExpired
from tornado import gen
from tornado.escape import to_unicode
from tornado.process import Subprocess


class Process(object):
    """
    Process handles starting and stopping an external process.
    """

    def __init__(self, log, proc_name, command, tty=False, env=None, log_suppress_regex=None,
                 log_replace_regex=None, color=True):
        """
        Initializes Process.

        Parameters
        ----------
        log : logging.Logger
            Logger.
        proc_name : str
            Process name (internal identifier for Jaffle).
        command : str
            Command-line string including command name and arguments.
        tty : bool
            Whether to require TTY emulation.
        env : dict{str: str}
            Environment variables.
        log_suppress_regex : list[str]
            Log suppress patterns.
        log_replace_regex : list[str]
            Log replace patterns.
        color : bool
            Whether to enable color output.
        """
        self.log = ProcessLogger(log, log_suppress_regex or [], log_replace_regex or [])
        self.proc_name = proc_name
        self.command = command
        self.tty = tty
        self.env = env or {}
        self.color = color

        self.proc = None

    def __repr__(self):
        """
        Returns string representation of Process.

        Returns
        -------
        repr : str
            String representation of Process.
        """
        return '<%s {proc_name: %s command: %s tty: %s env=%s}>' % (
            self.__class__.__name__, self.proc_name, self.command, self.tty, self.env
        )

    @gen.coroutine
    def start(self):
        """
        Starts the process.
        """
        self.log.info("Starting %s: '%s'", self.proc_name, self.command)

        env = os.environ.copy()
        env.update(**self.env)

        if self.tty:
            command = 'jaffle tty {} {!r}'.format(
                '' if self.color else '--disable-color', self.command
            )
        else:
            command = self.command

        # os.setpgrp() is required to prevent SIGINT propagation
        self.proc = Subprocess(shlex.split(command), env=env, stdin=None,
                               stdout=Subprocess.STREAM, stderr=Subprocess.STREAM,
                               preexec_fn=os.setpgrp)
        self.log.debug('proc: %s', self.proc)

        try:
            while True:
                line_bytes = yield self.proc.stdout.read_until(b'\n')
                line = to_unicode(line_bytes).strip('\r\n')
                self.log.info(line)
        except Exception as e:
            self.log.error(str(e))

    def stop(self):
        """
        Stops the process.
        """
        try:
            self.log.warning('Terminating %s', self.proc_name)
            os.killpg(os.getpgid(self.proc.proc.pid), signal.SIGTERM)
        except OSError:
            pass  # already dead

        try:
            self.proc.proc.wait(5)
        except TimeoutExpired:
            self.log.warning("Failed to terminate %s, killing it with SIGKILL", self.proc_name)
            os.killpg(os.getpgid(self.proc.proc.pid), signal.SIGKILL)

        self.proc = None


class ProcessLogger(object):
    """
    Logger for Process.
    """

    def __init__(self, log, suppress_regex=None, replace_regex=None):
        """
        Initializes ProcessLogger.

        Parameters
        ----------
        log : logging.Logger
            Logger.
        suppress_regex : list[str]
            Log suppress patterns.
        replace_regex : list[str]
            Log replace patterns.
        """
        self.log = log
        self.suppress_regex = suppress_regex or []
        self.replace_regex = replace_regex or []

    def emit(self, method, msg, *args, **kwargs):
        """
        Emits a log message.

        Parameters
        ----------
        method : function
            Logging function. (e.g.: ``self.error()``)
        msg : str
            Log message.
        args : list
            Arguments for the log message.
        kwargs : dict
            Keyword arguments for the log message
        """
        if not any([re.search(p, msg) for p in self.suppress_regex]):
            for pat in self.replace_regex:
                msg = re.sub(pat['from'], pat['to'], msg)
            method(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """
        Calls ``logging.Logger.debug()`` with given arguments.

        Parameters
        ----------
        msg : str
            Log message.
        args : list
            Arguments for the log message.
        kwargs : dict
            Keyword arguments for the log message
        """
        self.emit(self.log.debug, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Calls ``logging.Logger.info()`` with given arguments.

        Parameters
        ----------
        msg : str
            Log message.
        args : list
            Arguments for the log message.
        kwargs : dict
            Keyword arguments for the log message
        """
        self.emit(self.log.info, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Calls ``logging.Logger.warning()`` with given arguments.

        Parameters
        ----------
        msg : str
            Log message.
        args : list
            Arguments for the log message.
        kwargs : dict
            Keyword arguments for the log message
        """
        self.emit(self.log.warning, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Calls ``logging.Logger.error()`` with given arguments.

        Parameters
        ----------
        msg : str
            Log message.
        args : list
            Arguments for the log message.
        kwargs : dict
            Keyword arguments for the log message
        """
        self.emit(self.log.error, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Calls ``logging.Logger.critical()`` with given arguments.

        Parameters
        ----------
        msg : str
            Log message.
        args : list
            Arguments for the log message.
        kwargs : dict
            Keyword arguments for the log message
        """
        self.emit(self.log.critical, msg, *args, **kwargs)
