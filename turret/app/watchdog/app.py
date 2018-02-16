# -*- coding: utf-8 -*-

from pathlib import Path
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from ..base import BaseTurretApp


class WatchdogHandler(PatternMatchingEventHandler):

    def __init__(self, patterns=None, ignore_patterns=None,
                 ignore_directories=False, case_sensitive=False, events=[]):
        super().__init__(patterns=patterns, ignore_patterns=ignore_patterns,
                         ignore_directories=ignore_directories, case_sensitive=case_sensitive)
        self.events = events

    def on_any_event(self, event):
        self.events.append(event)


class WatchdogApp(BaseTurretApp):

    def __init__(self, app_name, turret_conf, turret_port, sessions, handlers=[]):
        super().__init__(app_name, turret_conf, turret_port, sessions)

        self.handlers = handlers

        self.events = []

        self.observer = Observer()

        for handler in self.handlers:
            wh = WatchdogHandler(patterns=handler.get('patterns', []),
                                 ignore_patterns=handler.get('ignore_patterns', []),
                                 ignore_directories=handler.get('ignore_directories', False),
                                 case_sensitive=handler.get('case_sensitive', False),
                                 events=self.events)
            self.observer.schedule(wh, str(Path.cwd()), recursive=True)

        self.observer.start()
