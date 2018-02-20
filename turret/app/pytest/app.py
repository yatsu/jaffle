# -*- coding: utf-8 -*-

import fnmatch
from pathlib import Path
import pytest
from _pytest import config
import re
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
        src_path = event['src_path']

        if any([fnmatch.fnmatchcase(src_path, p) for p in self.auto_test]):
            self.test(src_path)

        for glob, target in self.auto_test_map.items():
            # The pattern '...(?!\?\))' assumes that '*' is not followed by '?)'
            # because '?' and parenthesies are not allowed in the glob syntax
            pattern = re.sub(r'/', r'\/', re.sub(r'(?<!\\)\*(?!\?\))', r'([^/]*?)',
                                                 re.sub(r'(?<!\\)\*\*\/?', r'(.*?)', glob)))
            match = re.match(pattern, src_path)
            self.log.debug('glob: %s pattern: %s src_path: %s match: %s',
                           glob, pattern, src_path, match.groups() if match else False)
            if match:
                target_path = Path(target.format(*match.groups()).replace('//', '/'))
                if target_path.exists():
                    self.test(str(target_path))

    @capture_method_output
    def test(self, target):
        self.log.debug('pytest.main %s', self.args + [target])
        pytest.main(self.args + [target])
