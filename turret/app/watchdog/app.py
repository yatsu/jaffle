# -*- coding: utf-8 -*-

from functools import partial
from pathlib import Path
import shlex
import subprocess
from tornado import ioloop
from watchdog.observers import Observer
from ..base import BaseTurretApp
from .handler import WatchdogHandler


class WatchdogApp(BaseTurretApp):
    """
    Turret app which runs Watchdog in a kernel.
    """

    def __init__(self, app_name, turret_conf, turret_port, turret_status, handlers=[]):
        """
        Initializes WatchdogApp.

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
        handlers : list
            Watchdog handler definitions.
        """
        super().__init__(app_name, turret_conf, turret_port, turret_status)

        self.handlers = handlers
        self.observer = Observer()

        for handler in self.handlers:
            wh = WatchdogHandler(
                self.log, self.execute, ioloop.IOLoop.current(),
                patterns=handler.get('patterns', []),
                ignore_patterns=handler.get('ignore_patterns', []),
                ignore_directories=handler.get('ignore_directories', False),
                case_sensitive=handler.get('case_sensitive', False),
                uncache_modules=partial(self.uncache_modules, handler.get('uncache', [])),
                functions=handler.get('functions', []),
                debounce=handler.get('debounce', 0.0),
                throttle=handler.get('throttle', 0.0)
            )
            self.observer.schedule(wh, str(Path.cwd()), recursive=True)

        self.observer.start()

    def execute_command(self, command):
        """
        Executes a command.

        Parameters
        ----------
        command : str
            Command name and arguments separated by whitespaces.
        """
        self.log.info('Execute: %s', command)
        output = subprocess.check_output(shlex.split(command), shell=True)
        if len(output) > 0:
            self.log.info(output)
