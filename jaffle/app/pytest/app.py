# -*- coding: utf-8 -*-

from importlib import import_module
from pathlib import Path
import pkg_resources
import pytest
import re
from setuptools import find_packages
from ..base import BaseJaffleApp, capture_method_output, invalidate_module_cache_once
from .collect import collect_test_items
from .completer import PyTestCompleter
from .lexer import PyTestLexer


class PyTestRunnerApp(BaseJaffleApp):
    """
    Jaffle app which runs pytest in a kernel.
    """
    completer_class = PyTestCompleter

    lexer_class = PyTestLexer

    def __init__(self, app_name, jaffle_conf, jaffle_port, jaffle_status,
                 args=['-s', '-v'], plugins=[], auto_test=[], auto_test_map={},
                 invalidate_modules=None):
        """
        Initializes PyTestRunnerApp.

        Parameters
        ----------
        app_name : str
            App name defined in jaffle.hcl.
        jaffle_conf : dict
            Jaffle conf constructed from jaffle.hcl.
        jaffle_port : int
            TCP port for Jaffle ZMQ channel.
        jaffle_status : dict
            Jaffle status.
        args : list[str]
            pytest arguments.
        plugins : list[str]
            pytest plugins.
        auto_test : list[list]
            Test file names which should be executed when it is updated.
        auto_test_map : dict{str: str}
            Map from .py file patterns to test file patterns.
        invalidate_modules : list[str] or None
            Module names to be invalidated.
        """
        super().__init__(app_name, jaffle_conf, jaffle_port, jaffle_status)

        self.args = args
        self.plugins = plugins
        self.auto_test = auto_test
        self.auto_test_map = auto_test_map
        self.invalidate_modules = (invalidate_modules if invalidate_modules is not None
                                   else find_packages())

        # Suppress pytest warning for plugin: 'Module already imported'
        for plugin in pkg_resources.iter_entry_points('pytest11'):
            mod = import_module(plugin.module_name.split('.')[0])
            mod.__doc__ = 'PYTEST_DONT_REWRITE'

    @capture_method_output
    @invalidate_module_cache_once
    def handle_watchdog_event(self, event):
        """
        WatchdogApp callback to be executed on filessystem update.

        Parameters
        ----------
        event : dict
            Watdhdog event.
        """
        self.log.debug('event: %s', event)
        src_path = event['src_path']

        for glob in self.auto_test:
            regex = self.glob_to_regex(glob)
            match = re.match(regex, src_path)
            self.log.debug('auto_test glob: %s regex: %s src_path: %s match: %s',
                           glob, regex, src_path, match.groups() if match else None)
            if match:
                self.invalidate_module_cache(self.invalidate_modules)
                self.test(src_path)

        for glob, target in self.auto_test_map.items():
            regex = self.glob_to_regex(glob)
            match = re.match(regex, src_path)
            self.log.debug('auto_test_map glob: %s regex: %s src_path: %s match: %s',
                           glob, regex, src_path, match.groups() if match else None)
            if match:
                target_path = Path(target.format(*match.groups()).replace('//', '/'))
                if target_path.exists():
                    self.invalidate_module_cache(self.invalidate_modules)
                    self.test(str(target_path))

    @capture_method_output
    def test(self, target):
        """
        Executes pytest.

        Parameters
        ----------
        target : str
            pytest target
            (e.g. ``example/tests/text_example.py::test_example``).
        """
        self.log.debug('pytest.main %s', self.args + [target])
        pytest.main(self.args + [target])

    def glob_to_regex(self, glob):
        """
        Converts a glob pattern ``**`` and ``*`` to a regular expression.

        Parameters
        ----------
        glob : str
            Glob pattern which contains ``**`` and/or ``*``.

        Returns
        -------
        regex : str
            Regular expression converted from a glob pattern.
        """
        # The pattern '...(?!\?\))' assumes that '*' is not followed by '?)'
        # because '?' and parenthesies are not allowed in the glob syntax
        return re.sub(r'/', r'\/', re.sub(r'(?<!\\)\*(?!\?\))', r'([^/]*?)',
                                          re.sub(r'(?<!\\)\*\*\/?', r'(.*?)', glob)))

    @capture_method_output
    def collect(self):
        """
        Collects test modules.

        Returns
        -------
        test_items : list[str]
            Test items (e.g. ['example/tests/test_example.py::test_example'])
        """
        return collect_test_items()

    @classmethod
    def command_to_code(self, app_name, command):
        """
        Converts a command comes from ``jaffle attach pyteet`` to a code to be
        executed.

        Parameters
        ----------
        app_name : str
            App name defined in jaffle.hcl.
        command : str
            Command name received from the shell of ``jaffle attach``.

        Returns
        -------
        code : str
            Code to be executed.
        """
        return '{}.test({!r})'.format(app_name, command)
