# -*- coding: utf-8 -*-

import logging


class JaffleAppLogHandler(logging.StreamHandler):
    """
    Log handler for Jaffle apps, which sends log records to the Jaffle server's
    ZeroMQ channel.
    """
    def __init__(self, app_name, get_stream):
        """
        Initializes JaffleAppLogHandler.

        Parameters
        ----------
        app_name : str
            App name defined in jaffle.hcl.
        get_stream : function
            Function to get Jaffle ZeroMQ stream.
        """
        super().__init__()

        self.app_name = app_name
        self.get_stream = get_stream

    def emit(self, record):
        """
        Sends a log record to the Jaffle servers' ZeroMQ channel.

        Parameters
        ----------
        record : logging.LogRecord
            Log record.
        """
        stream = self.get_stream()
        if stream:
            stream.send_json({
                'app_name': self.app_name,
                'type': 'log',
                'payload': {
                    'logger': record.name,
                    'levelname': record.levelname,
                    'message': self.format(record)
                }
            })
