# -*- coding: utf-8 -*-

from functools import partial
from pathlib import Path
from tornado import gen, ioloop
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
from .base import BaseTurretApp


def event_to_dict(event):
    return {
        'event_type': event.event_type,
        'src_path': str(Path(event.src_path).relative_to(Path.cwd())),
        'is_directory': event.is_directory
    }


class WatchdogHandler(PatternMatchingEventHandler):

    def __init__(self, log, execute, functions=[], patterns=None, ignore_patterns=None,
                 ignore_directories=False, case_sensitive=False, uncache_modules=None):
        super().__init__(patterns=patterns, ignore_patterns=ignore_patterns,
                         ignore_directories=ignore_directories, case_sensitive=case_sensitive)

        self.log = log
        self.execute = execute
        self.functions = functions
        self.uncache_modules = uncache_modules

    def on_any_event(self, event):
        @gen.coroutine
        def handle_event():
            if self.uncache_modules:
                self.log.debug('uncache_modules')
                self.uncache_modules()

            event_dict = event_to_dict(event)
            # self.log.info('%s: %s', event_dict['event_type'], event_dict['src_path'])
            self.log.debug('event: %s', event_dict)
            for function in self.functions:
                try:
                    yield gen.maybe_future(self.execute(function, event=event_dict))
                except Exception as e:
                    self.log.error('Event handling error: %s', str(e))

        ioloop.IOLoop.current().add_callback(handle_event)


class WatchdogApp(BaseTurretApp):

    def __init__(self, app_name, turret_conf, turret_port, turret_status, handlers=[]):
        super().__init__(app_name, turret_conf, turret_port, turret_status)

        self.handlers = handlers
        self.observer = Observer()

        for handler in self.handlers:
            wh = WatchdogHandler(
                self.log, self.execute,
                handler.get('functions', []),
                patterns=handler.get('patterns', []),
                ignore_patterns=handler.get('ignore_patterns', []),
                ignore_directories=handler.get('ignore_directories', False),
                case_sensitive=handler.get('case_sensitive', False),
                uncache_modules=partial(self.uncache_modules, handler.get('uncache', []))
            )
            self.observer.schedule(wh, str(Path.cwd()), recursive=True)

        self.observer.start()
