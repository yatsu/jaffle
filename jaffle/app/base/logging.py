# -*- coding: utf-8 -*-

import logging
from tornado import ioloop
import zmq
from zmq.eventloop import zmqstream


class JaffleAppLogHandler(logging.StreamHandler):
    """
    Log handler for Jaffle apps, which sends log records to the Jaffle server's
    ZeroMQ channel.
    """
    def __init__(self, app_name, jaffle_port, main_io_loop=None):
        """
        Initializes JaffleAppLogHandler.

        Parameters
        ----------
        app_name : str
            App name defined in jaffle.hcl.
        jaffle_port : int
            TCP port for Jaffle ZMQ channel.
        main_io_loop : tornado.ioloop.IOLoop
            IO loop of the main thread.
        """
        super().__init__()

        self.app_name = app_name
        self.main_io_loop = main_io_loop or ioloop.IOLoop.current()

        ctx = zmq.Context.instance()
        socket = ctx.socket(zmq.PUSH)
        socket.connect('tcp://127.0.0.1:{0}'.format(jaffle_port))
        self.stream = zmqstream.ZMQStream(socket, self.main_io_loop)

    def emit(self, record):
        """
        Sends a log record to the Jaffle servers' ZeroMQ channel.

        Parameters
        ----------
        record : logging.LogRecord
            Log record.
        """
        def emit_log_record():
            self.stream.send_json({
                'app_name': self.app_name,
                'type': 'log',
                'payload': {
                    'logger': record.name,
                    'levelname': record.levelname,
                    'message': self.format(record)
                }
            })

        self.main_io_loop.add_callback(emit_log_record)  # emit in the main thread
