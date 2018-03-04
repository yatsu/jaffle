# -*- coding: utf-8 -*-

from contextlib import redirect_stderr, redirect_stdout
from functools import wraps
import io
import logging
import sys


class OutputCapturer(io.StringIO):
    """
    Output stream capturer, which indended to be used as a replacement of
    ``sys.stdout`` and ``sys.stderr``.
    """
    def __init__(self, log, log_level=logging.INFO, std=None):
        """
        Initializes OutputCapturer.
        If ``std`` is specified, the output echoes through it.

        Parameters
        ----------
        log : logging.Logger
            Logger.
        log_level : int
            Log level.
        std : ipykernel.iostream.OutStream
            Original output stream.
        """
        super().__init__()
        self.log = log
        self.log_level = log_level
        self.std = std

    def write(self, buf):
        """
        Writes to the stream.

        Parameters
        ----------
        buf : str
            String buffer to be written.
        """
        if self.std:
            self.std.write(buf)
        for line in buf.rstrip().splitlines():
            text = line.rstrip()
            if len(text) > 0:
                self.log.log(self.log_level, text)

    def flush(self):
        """
        Flushes the stream.
        """
        if self.std:
            self.std.flush()


def capture_method_output(func):
    """
    Decorator to a Turret app method to capture output and send it to the
    logger.
    ``stdout`` and ``stderr`` are redirected as ``logging.INFO`` and
    ``logging.WARNING`` respectively.

    Parameters
    ----------
    func : function
        Function to be wrapped.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Prevent nested capturing
        if isinstance(sys.stdout, OutputCapturer):
            return func(self, *args, **kwargs)

        stdout = OutputCapturer(self.log, logging.INFO, sys.stdout)
        stderr = OutputCapturer(self.log, logging.WARNING, sys.stderr)

        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                return func(self, *args, **kwargs)

    return wrapper
