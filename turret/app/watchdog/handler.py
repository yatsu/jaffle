# -*- coding: utf-8 -*-

from pathlib import Path
from tornado import gen
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

    def __init__(self, log, execute, ioloop, patterns=None, ignore_patterns=None,
                 ignore_directories=False, case_sensitive=False, uncache_modules=None,
                 functions=[], debounce=0.0, throttle=0.0):
        """
        Initializes WatchdogHandler.

        Parameters
        ----------
        log : logging.Logger
            Logger.
        execute : function
            Function to execute the code.
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
        functions : list[str]
            Functions to be called on filesystem events.
        """
        super().__init__(patterns=patterns, ignore_patterns=ignore_patterns,
                         ignore_directories=ignore_directories, case_sensitive=case_sensitive)

        self.log = log
        self.execute = execute
        self.ioloop = ioloop
        self.uncache_modules = uncache_modules
        self.functions = functions
        self.debounce = debounce
        self.throttle = throttle

        self._timeout = None
        self._in_throttle = False

    def on_any_event(self, event):
        """
        Event handler for Watchdog filesystem events.
        Executes the handling in the main ioloop.

        Parameters
        ----------
        event : watchdog.events.FileSystemEvent
            Watchdog filesystem event.
        """
        def handle_event():
            if self.uncache_modules:
                self.log.debug('uncache_modules')
                self.uncache_modules()

            event_dict = _event_to_dict(event)
            self.log.debug('event: %s', event_dict)

            @gen.coroutine
            def call_funcs():
                for function in self.functions:
                    try:
                        yield self.execute(function, event=event_dict)
                    except Exception as e:
                        self.log.error('Event handling error: %s', str(e))

            if self.debounce > 0.0:
                if self._timeout:
                    self.ioloop.remove_timeout(self._timeout)
                self._timeout = self.ioloop.call_later(self.debounce, call_funcs)
            else:
                if self.throttle > 0.0:
                    if self._in_throttle:
                        return

                    def unthrottle():
                        self._in_throttle = False

                    self._in_throttle = True
                    self._timeout = self.ioloop.call_later(self.throttle, unthrottle)

                self.ioloop.add_callback(call_funcs)

        self.ioloop.add_callback(handle_event)
