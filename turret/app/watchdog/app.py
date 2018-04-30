# -*- coding: utf-8 -*-

from functools import partial
from pathlib import Path
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
                ioloop.IOLoop.current(),
                self.execute_code,
                self.execute_job,
                self.log,
                patterns=handler.get('patterns', []),
                ignore_patterns=handler.get('ignore_patterns', []),
                ignore_directories=handler.get('ignore_directories', False),
                case_sensitive=handler.get('case_sensitive', False),
                invalidate_module_cache=partial(self.invalidate_module_cache,
                                                handler.get('invalidate_modules', [])),
                code_blocks=handler.get('code_blocks', []),
                jobs=handler.get('jobs', []),
                debounce=handler.get('debounce', 0.0),
                throttle=handler.get('throttle', 0.0)
            )

            watch_path = handler.get('watch_path', '.')
            if Path(watch_path).is_absolute():
                observe_path = str(watch_path)
            else:
                observe_path = str(Path.cwd() / watch_path)

            self.observer.schedule(wh, observe_path, recursive=True)

        self.observer.start()
