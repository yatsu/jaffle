# -*- coding: utf-8 -*-

import fnmatch
import pytest
from _pytest import config
from ..base import BaseTurretApp, capture_method_output


create_terminal_writer_org = config.create_terminal_writer


def create_terminal_writer(config, *args, **kwargs):
    tw = create_terminal_writer_org(config, *args, **kwargs)
    tw.fullwidth -= 32
    return tw


# Patch create_terminal_writer() to shorten the screen width to fit the
# log message.
# This should be configurable...
setattr(config, 'create_terminal_writer', create_terminal_writer)


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
            pytest.main(self.args + [event['src_path']])
