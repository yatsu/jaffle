# -*- coding: utf-8 -*-

import os
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

    def __init__(self, log, proc_name, command, env={}):
        """
        Initializes Process.

        Parameters
        ----------
        log : logging.Logger
            Logger.
        proc_name : str
            Process name (internal identifier for Turret).
        comand : str
            Command-line string including command name and arguments.
        env : dict{str: str}
            Environment variables.
        """
        self.log = log
        self.proc_name = proc_name
        self.command = command
        self.env = env
        self.proc = None

    @gen.coroutine
    def start(self):
        """
        Starts the process.
        """
        self.log.info("Starting %s: '%s'", self.proc_name, self.command)

        env = os.environ.copy()
        env.update(**self.env)

        # os.setpgrp() is required to prevent SIGINT propagation
        self.proc = Subprocess(shlex.split(self.command), env=env,
                               stdin=None, stdout=Subprocess.STREAM, stderr=Subprocess.STREAM,
                               preexec_fn=os.setpgrp)
        self.log.debug('proc: %s', self.proc)

        try:
            while True:
                line = yield self.proc.stdout.read_until(b'\n')
                self.log.info(to_unicode(line).rstrip('\n'))
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
