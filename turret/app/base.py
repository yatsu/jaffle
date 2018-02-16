# -*- coding: utf-8 -*-

import json
import logging
from tornado.escape import utf8
import zmq


class TurretAppLogger(object):

    def __init__(self, app_name, socket):
        self.app_name = app_name
        self.socket = socket

    def _send(self, level, msg, *args, **kwargs):
        self.socket.send(utf8(json.dumps({
            'app_name': self.app_name,
            'type': 'log',
            'level': level,
            'msg': msg,
            'args': args,
            'kwargs': kwargs
        })))

    def critical(self, msg, *args, **kwargs):
        self._send(logging.CRITICAL, msg, *args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        self._send(logging.FATAL, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._send(logging.ERROR, msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self._send(logging.WARN, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._send(logging.WARNING, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._send(logging.INFO, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._send(logging.DEBUG, msg, *args, **kwargs)


class BaseTurretApp(object):

    def __init__(self, app_name, turret_conf, turret_port, sessions):
        self.app_name = app_name
        self.turret_port = turret_port
        self.turret_conf = turret_conf
        self.sessions = sessions

        ctx = zmq.Context.instance()
        self.turret_socket = ctx.socket(zmq.DEALER)
        self.turret_socket.connect('tcp://127.0.0.1:{0}'.format(self.turret_port))

        self.log = TurretAppLogger(app_name, self.turret_socket)

    def execute(command):
        # execute command on local or remote
        pass
