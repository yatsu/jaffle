# -*- coding: utf-8 -*-

import logging


class TurretAppLogHandler(logging.StreamHandler):
    """
    Log handler for Turret apps, which sends log records to the Turret server's
    ZeroMQ channel.
    """
    def __init__(self, app_name, get_stream):
        """
        Initializes TurretAppLogHandler.

        Parameters
        ----------
        app_name : str
            App name defined in turret.hcl.
        get_stream : function
            Function to get Turret ZeroMQ stream.
        """
        super().__init__()

        self.app_name = app_name
        self.get_stream = get_stream

    def emit(self, record):
        """
        Sends a log record to the Turret servers' ZeroMQ channel.

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
