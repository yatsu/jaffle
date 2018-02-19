# -*- coding: utf-8 -*-

import logging
import zmq


class TurretAppLogHandler(logging.StreamHandler):

    def __init__(self, app_name, socket):
        super().__init__()

        self.app_name = app_name
        self.socket = socket

    def emit(self, record):
        self.socket.send_json({
            'app_name': self.app_name,
            'type': 'log',
            'payload': dict(record.__dict__, args_type=type(record.args).__name__)
        })


class BaseTurretApp(object):

    def __init__(self, app_name, turret_conf, turret_port, sessions, namespace={}):
        self.app_name = app_name
        self.turret_port = turret_port
        self.turret_conf = turret_conf
        self.sessions = sessions
        self.namespace = namespace

        ctx = zmq.Context.instance()
        self.turret_socket = ctx.socket(zmq.PUSH)
        self.turret_socket.connect('tcp://127.0.0.1:{0}'.format(self.turret_port))

        self.log = logging.getLogger(app_name)
        level = turret_conf['app'][app_name].get('logger', {}).get('level', 'info')
        self.log.setLevel(getattr(logging, level.upper()))
        handler = TurretAppLogHandler(app_name, self.turret_socket)
        self.log.addHandler(handler)

    def execute(command):
        # execute command on local or remote
        pass
