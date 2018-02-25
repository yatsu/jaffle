# -*- coding: utf-8 -*-

from pathlib import Path
from prompt_toolkit.completion import Completer, Completion
import pytest
from _pytest import config
import re
from setuptools import find_packages
from .base import BaseTurretApp, capture_method_output, uncache_modules_once


create_terminal_writer_org = config.create_terminal_writer


def create_terminal_writer(config, *args, **kwargs):
    tw = create_terminal_writer_org(config, *args, **kwargs)
    tw.fullwidth -= 32
    return tw


# Patch create_terminal_writer() to shorten the screen width to fit the
# log message.
# This should be configurable...
setattr(config, 'create_terminal_writer', create_terminal_writer)


class TestCollector(object):

    def __init__(self):
        self.test_items = []

    def pytest_collection_modifyitems(self, items):
        for item in items:
            self.test_items.append(item.nodeid)


class PyTestCompleter(Completer):

    def __init__(self):
        test_collector = TestCollector()
        pytest.main(['--collect-only'], plugins=[test_collector])
        self.test_items = test_collector.test_items

    def get_completions(self, document, complete_event):
        for m in [i for i in self.test_items if i.startswith(document.text)]:
            yield Completion(m, start_position=-document.cursor_position)


class PyTestRunnerApp(BaseTurretApp):

    completer_class = PyTestCompleter

    def __init__(self, app_name, turret_conf, turret_port, turret_status,
                 args=['-s', '-v'], plugins=[], auto_test=[], auto_test_map={},
                 uncache=[]):
        super().__init__(app_name, turret_conf, turret_port, turret_status)

        self.args = args
        self.plugins = plugins
        self.auto_test = auto_test
        self.auto_test_map = auto_test_map
        self.uncache = uncache or find_packages()

    @capture_method_output
    @uncache_modules_once
    def handle_watchdog_event(self, event):
        self.log.debug('event: %s', event)
        src_path = event['src_path']

        for glob in self.auto_test:
            regex = self.glob_to_regex(glob)
            match = re.match(regex, src_path)
            self.log.debug('auto_test glob: %s regex: %s src_path: %s match: %s',
                           glob, regex, src_path, match.groups() if match else None)
            if match:
                self.uncache_modules(self.uncache)
                self.test(src_path)

        for glob, target in self.auto_test_map.items():
            regex = self.glob_to_regex(glob)
            match = re.match(regex, src_path)
            self.log.debug('auto_test_map glob: %s regex: %s src_path: %s match: %s',
                           glob, regex, src_path, match.groups() if match else None)
            if match:
                target_path = Path(target.format(*match.groups()).replace('//', '/'))
                if target_path.exists():
                    self.uncache_modules(self.uncache)
                    self.test(str(target_path))

    @capture_method_output
    def test(self, target):
        self.log.debug('pytest.main %s', self.args + [target])
        pytest.main(self.args + [target])

    def glob_to_regex(self, glob):
        # The pattern '...(?!\?\))' assumes that '*' is not followed by '?)'
        # because '?' and parenthesies are not allowed in the glob syntax
        return re.sub(r'/', r'\/', re.sub(r'(?<!\\)\*(?!\?\))', r'([^/]*?)',
                                          re.sub(r'(?<!\\)\*\*\/?', r'(.*?)', glob)))

    @classmethod
    def command_to_code(self, app_name, command):
        return '{}.test({!r})'.format(app_name, command)
