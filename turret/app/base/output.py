# -*- coding: utf-8 -*-

from contextlib import redirect_stdout
from functools import wraps
import io
import logging
import sys

try:
    from contextlib import redirect_stderr
except ImportError:
    # Python < 3.5
    class redirect_stderr:

        def __init__(self, new_target):
            self._new_target = new_target
            self._old_targets = []

        def __enter__(self):
            self._old_targets.append(sys.stderr)
            sys.stderr = self._new_target
            return self._new_target

        def __exit__(self, exctype, excinst, exctb):
            sys.stderr = self._old_targets.pop()


class OutputLogger(io.StringIO):
    """
    Output stream logger, which can be used as a replacement of ``sys.stdout``
    and ``sys.stderr``.
    """
    def __init__(self, log, log_level=logging.INFO, org_io=None):
        """
        Initializes OutputLogger.
        If ``org_io`` is specified, the output echoes through it.

        Parameters
        ----------
        log : logging.Logger
            Logger.
        log_level : int
            Log level.
        org_io : io.TextIOBase
            Original output stream.
            If it is not None, the output will also be written to it.
        """
        super().__init__()
        self.log = log
        self.log_level = log_level
        self.org_io = org_io

    def write(self, buf):
        """
        Writes to the stream.

        Parameters
        ----------
        buf : str
            String buffer to be written.
        """
        if self.org_io:
            self.org_io.write(buf)
        for line in buf.rstrip().splitlines():
            text = line.rstrip()
            if len(text) > 0:
                self.log.log(self.log_level, text)

    def flush(self):
        """
        Flushes the stream.
        """
        if self.org_io:
            self.org_io.flush()


def capture_method_output(method):
    """
    Decorator for an app method to capture standard output and redirects it to
    the logger. ``stdout`` and ``stderr`` are logged with level ``INFO`` and
    ``WARNING`` respectively.

    Parameters
    ----------
    method : function
        Method to be wrapped.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        # Prevent nested capture
        if isinstance(sys.stdout, OutputLogger):
            return method(self, *args, **kwargs)

        stdout = OutputLogger(self.log, logging.INFO, sys.stdout)
        stderr = OutputLogger(self.log, logging.WARNING, sys.stderr)

        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                return method(self, *args, **kwargs)

    return wrapper
