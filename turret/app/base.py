# -*- coding: utf-8 -*-


class BaseTurretApp(object):

    def __init__(self, app_name, turret_conf, sessions):
        self.app_name = app_name
        self.turret_conf = turret_conf
        self.sessions = sessions

    def execute(command):
        # execute command on local or remote
        pass
