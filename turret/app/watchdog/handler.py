# -*- coding: utf-8 -*-

from pathlib import Path
from tornado import gen, ioloop
from watchdog.events import PatternMatchingEventHandler


def _event_to_dict(event):
    """
    Converts an Watchdog filesystem event to a dict.

    Parameters
    ----------
    event : watchdog.events.FileSystemEvent
        Watchdog filesystem event.

    Returns
    -------
    event_dict : dict
        Dict representation of the Watchdog filesystem event.
    """
    return {
        'event_type': event.event_type,
        'src_path': str(Path(event.src_path).relative_to(Path.cwd())),
        'is_directory': event.is_directory
    }


class WatchdogHandler(PatternMatchingEventHandler):
    """
    Watchdog event handler for Turret.
    """

    def __init__(self, log, execute, functions=[], patterns=None, ignore_patterns=None,
                 ignore_directories=False, case_sensitive=False, uncache_modules=None):
        """
        Initializes WatchdogHandler.

        Parameters
        ----------
        log : logging.Logger
            Logger.
        execute : function
            Function to execute the code.
        functions : list[str]
            Functions to be called on filesystem events.
        patterns : list[str]
            File path pattern to be watched (glob pattern for ``fnmatch``).
        ignore_patterns : list[str]
            File path pattern to be ignored (glob pattern for ``fnmatch``).
        ignore_directories : bool
            Whether to ignore directories.
        case_sensitive : bool
            Case sensitive or not.
        uncache_modules : list[str]
            Module names to be uncached.
        """
        super().__init__(patterns=patterns, ignore_patterns=ignore_patterns,
                         ignore_directories=ignore_directories, case_sensitive=case_sensitive)

        self.log = log
        self.execute = execute
        self.functions = functions
        self.uncache_modules = uncache_modules

    def on_any_event(self, event):
        """
        Event handler for Watchdog filesystem events.
        Executes the handling in the main ioloop.

        Parameters
        ----------
        event : watchdog.events.FileSystemEvent
            Watchdog filesystem event.
        """
        @gen.coroutine
        def handle_event():
            if self.uncache_modules:
                self.log.debug('uncache_modules')
                self.uncache_modules()

            event_dict = _event_to_dict(event)
            # self.log.info('%s: %s', event_dict['event_type'], event_dict['src_path'])
            self.log.debug('event: %s', event_dict)
            for function in self.functions:
                try:
                    yield gen.maybe_future(self.execute(function, event=event_dict))
                except Exception as e:
                    self.log.error('Event handling error: %s', str(e))

        ioloop.IOLoop.current().add_callback(handle_event)
