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

    def __init__(self, ioloop, execute_code, execute_job, log,
                 patterns=None, ignore_patterns=None, ignore_directories=False,
                 case_sensitive=False, invalidate_module_cache=None,
                 functions=[], jobs=[], debounce=0.0, throttle=0.0):
        """
        Initializes WatchdogHandler.

        Parameters
        ----------
        execute_code : function
            Function to execute a code.
        execute_job : function
            Function to execute a job.
        log : logging.Logger
            Logger.
        patterns : list[str]
            File path pattern to be watched (glob pattern for ``fnmatch``).
        ignore_patterns : list[str]
            File path pattern to be ignored (glob pattern for ``fnmatch``).
        ignore_directories : bool
            Whether to ignore directories.
        case_sensitive : bool
            Case sensitive or not.
        invalidate_module_cache : function or None
            Cache invalidation function.
        functions : list[str]
            Functions to be executed on receiving filesystem events.
        jobs : list[str]
            Jobs to be executed on receiving filesystem events.
        debounce : float
            Debounce time in seconds. If it is 0.0, debounce is disabled.
        throttle : float
            Throttle time in seconds. If it is 0.0, throttle is disabled.
        """
        super().__init__(patterns=patterns, ignore_patterns=ignore_patterns,
                         ignore_directories=ignore_directories, case_sensitive=case_sensitive)

        self.ioloop = ioloop
        self.execute_code = execute_code
        self.execute_job = execute_job
        self.log = log
        self.invalidate_module_cache = invalidate_module_cache
        self.functions = functions
        self.jobs = jobs
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
            if self.invalidate_module_cache:
                self.invalidate_module_cache()

            event_dict = _event_to_dict(event)
            self.log.debug('event: %s', event_dict)

            @gen.coroutine
            def execute_callbacks():
                for function in self.functions:
                    try:
                        yield self.execute_code(function, event=event_dict)
                    except Exception as e:
                        self.log.exception('Code execution error: %s', e)

                for job in self.jobs:
                    try:
                        yield self.execute_job(job)
                    except Exception as e:
                        self.log.exception('Job execution error: %s', e)

            if self.debounce > 0.0:
                if self._timeout:
                    self.ioloop.remove_timeout(self._timeout)
                self._timeout = self.ioloop.call_later(self.debounce, execute_callbacks)
            else:
                if self.throttle > 0.0:
                    if self._in_throttle:
                        return

                    def unthrottle():
                        self._in_throttle = False

                    self._in_throttle = True
                    self._timeout = self.ioloop.call_later(self.throttle, unthrottle)

                self.ioloop.add_callback(execute_callbacks)

        self.ioloop.add_callback(handle_event)
