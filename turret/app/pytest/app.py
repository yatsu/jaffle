# -*- coding: utf-8 -*-

import fnmatch
import pytest
from ..base import BaseTurretApp, capture_method_output


class PyTestRunnerApp(BaseTurretApp):

    def __init__(self, app_name, turret_conf, turret_port, sessions,
                 args=['-s', '-v'], plugins=[], auto_test=[], auto_test_map={}):
        super().__init__(app_name, turret_conf, turret_port, sessions)

        self.args = args
        self.plugins = plugins
        self.auto_test = auto_test
        self.auto_test_map = auto_test_map

    @capture_method_output
    def handle_watchdog_event(self, event):
        self.log.debug('event: %s', event)

        if any([fnmatch.fnmatchcase(event['src_path'], p) for p in self.auto_test]):
            self.log.debug('pytest.main %s', self.args + [event['src_path']])
            result = pytest.main(self.args + [event['src_path']])
            self.log.debug('result: %s', result)
