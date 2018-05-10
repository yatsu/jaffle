# -*- coding: utf-8 -*-

import re


class ProcessLogger(object):
    """
    Logger for Process.
    """

    def __init__(self, log, suppress_regex=None, replace_regex=None):
        """
        Initializes ProcessLogger.

        Parameters
        ----------
        log : logging.Logger
            Logger.
        suppress_regex : list[str]
            Log suppress patterns.
        replace_regex : list[str]
            Log replace patterns.
        """
        self.log = log
        self.suppress_regex = suppress_regex or []
        self.replace_regex = replace_regex or []

    def emit(self, method, msg, *args, **kwargs):
        """
        Emits a log message.

        Parameters
        ----------
        method : function
            Logging function. (e.g.: ``self.error()``)
        msg : str
            Log message.
        args : list
            Arguments for the log message.
        kwargs : dict
            Keyword arguments for the log message
        """
        if not any([re.search(p, msg) for p in self.suppress_regex]):
            for pat in self.replace_regex:
                msg = re.sub(pat['from'], pat['to'], msg)
            method(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """
        Calls ``logging.Logger.debug()`` with given arguments.

        Parameters
        ----------
        msg : str
            Log message.
        args : list
            Arguments for the log message.
        kwargs : dict
            Keyword arguments for the log message
        """
        self.emit(self.log.debug, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Calls ``logging.Logger.info()`` with given arguments.

        Parameters
        ----------
        msg : str
            Log message.
        args : list
            Arguments for the log message.
        kwargs : dict
            Keyword arguments for the log message
        """
        self.emit(self.log.info, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Calls ``logging.Logger.warning()`` with given arguments.

        Parameters
        ----------
        msg : str
            Log message.
        args : list
            Arguments for the log message.
        kwargs : dict
            Keyword arguments for the log message
        """
        self.emit(self.log.warning, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Calls ``logging.Logger.error()`` with given arguments.

        Parameters
        ----------
        msg : str
            Log message.
        args : list
            Arguments for the log message.
        kwargs : dict
            Keyword arguments for the log message
        """
        self.emit(self.log.error, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Calls ``logging.Logger.critical()`` with given arguments.

        Parameters
        ----------
        msg : str
            Log message.
        args : list
            Arguments for the log message.
        kwargs : dict
            Keyword arguments for the log message
        """
        self.emit(self.log.critical, msg, *args, **kwargs)
