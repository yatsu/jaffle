# -*- coding: utf-8 -*-

from functools import partial
from pathlib import Path
from tornado import ioloop
from watchdog.observers import Observer
from ...utils import bool_value
from ..base import BaseJaffleApp
from .handler import WatchdogHandler


class WatchdogApp(BaseJaffleApp):
    """
    Jaffle app which runs Watchdog in a kernel.
    """

    def __init__(self, app_conf_data):
        """
        Initializes WatchdogApp.

        Parameters
        ----------
        app_conf_data : dict
            App configuration data.
        """
        super().__init__(app_conf_data)

        self.observer = Observer()

        for handler in self.options.get_raw('handlers', []):
            wh = WatchdogHandler(
                ioloop.IOLoop.current(),
                self.execute_code,
                self.execute_job,
                self.log,
                patterns=handler.get('patterns', []),
                ignore_patterns=handler.get('ignore_patterns', []),
                ignore_directories=bool_value(handler.get('ignore_directories', False)),
                case_sensitive=bool_value(handler.get('case_sensitive', False)),
                clear_module_cache=partial(self.clear_module_cache,
                                           handler.get('clear_cache', [])),
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
