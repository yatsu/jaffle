# -*- coding: utf-8 -*-

import logging


class TurretAppLogHandler(logging.StreamHandler):
    """
    Log handler for Turret apps, which sends log records to the Turret server's
    ZeroMQ channel.
    """
    def __init__(self, app_name, socket):
        """
        Initializes TurretAppLogHandler.

        Parameters
        ----------
        app_name : str
            App name defined in turret.hcl.
        socket : zmq.Socket
            ZeroMQ socket, to which log records will be sent.
        """
        super().__init__()

        self.app_name = app_name
        self.socket = socket

    def emit(self, record):
        """
        Sends a log record to the Turret servers' ZeroMQ channel.

        Parameters
        ----------
        record : logging.LogRecord
            Log record.
        """
        self.socket.send_json({
            'app_name': self.app_name,
            'type': 'log',
            'payload': {
                'levelname': record.levelname,
                'message': self.format(record)
            }
        })
