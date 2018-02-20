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

    def __init__(self, log, function, namespace, patterns=None, ignore_patterns=None,
                 ignore_directories=False, case_sensitive=False):
        super().__init__(patterns=patterns, ignore_patterns=ignore_patterns,
                         ignore_directories=ignore_directories, case_sensitive=case_sensitive)

        self.log = log
        self.function = function
        self.namespace = namespace

    def on_any_event(self, event):
        self.log.debug('event: %s', event_to_dict(event))
        if self.function:
            try:
                self._get_func(self.function, self.namespace)(event_to_dict(event))
            except Exception as e:
                self.log.error('Event handling error: %s', str(e))

    def _get_func(self, func_name, namespace):
        comps = func_name.split('.')
        if isinstance(namespace, dict):
            var = namespace[comps[0]]
        else:
            var = getattr(namespace, comps[0])
        if len(comps) == 1:
            return var
        return self._get_func(comps[1], var)


class WatchdogApp(BaseTurretApp):

    def __init__(self, app_name, turret_conf, turret_port, sessions, namespace, handlers=[]):
        super().__init__(app_name, turret_conf, turret_port, sessions, namespace)

        self.handlers = handlers
        self.observer = Observer()

        for handler in self.handlers:
            wh = WatchdogHandler(self.log, handler.get('function'), self.namespace,
                                 patterns=handler.get('patterns', []),
                                 ignore_patterns=handler.get('ignore_patterns', []),
                                 ignore_directories=handler.get('ignore_directories', False),
                                 case_sensitive=handler.get('case_sensitive', False))
            self.observer.schedule(wh, str(Path.cwd()), recursive=True)

        self.observer.start()
