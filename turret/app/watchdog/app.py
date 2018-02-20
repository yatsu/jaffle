# -*- coding: utf-8 -*-

from pathlib import Path
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from ..base import BaseTurretApp


def event_to_dict(event):
    return {
        'event_type': event.event_type,
        'src_path': str(Path(event.src_path).relative_to(Path.cwd())),
        'is_directory': event.is_directory
    }


class WatchdogHandler(PatternMatchingEventHandler):

    def __init__(self, log, execute, function, patterns=None, ignore_patterns=None,
                 ignore_directories=False, case_sensitive=False):
        super().__init__(patterns=patterns, ignore_patterns=ignore_patterns,
                         ignore_directories=ignore_directories, case_sensitive=case_sensitive)

        self.log = log
        self.execute = execute
        self.function = function

    def on_any_event(self, event):
        event_dict = event_to_dict(event)
        self.log.info('%s: %s', event_dict['event_type'], event_dict['src_path'])
        self.log.debug('event: %s', event_dict)
        if self.function:
            try:
                self.execute(self.function, event=event_dict)
            except Exception as e:
                self.log.error('Event handling error: %s', str(e))


class WatchdogApp(BaseTurretApp):

    def __init__(self, app_name, turret_conf, turret_port, sessions, handlers=[]):
        super().__init__(app_name, turret_conf, turret_port, sessions)

        self.handlers = handlers
        self.observer = Observer()

        for handler in self.handlers:
            wh = WatchdogHandler(self.log, self.execute,
                                 handler.get('function'),
                                 patterns=handler.get('patterns', []),
                                 ignore_patterns=handler.get('ignore_patterns', []),
                                 ignore_directories=handler.get('ignore_directories', False),
                                 case_sensitive=handler.get('case_sensitive', False))
            self.observer.schedule(wh, str(Path.cwd()), recursive=True)

        self.observer.start()
