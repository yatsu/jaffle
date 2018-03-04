# -*- coding: utf-8 -*-

from importlib import import_module
from pathlib import Path
import pkg_resources
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.layout.lexers import Lexer
from pygments.token import Token
import pytest
from _pytest import config
import re
from setuptools import find_packages
import sys
from ..base import BaseTurretApp, capture_method_output, uncache_modules_once


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

    def __init__(self, app_name, app_conf, client):
        self.app_name = app_name
        self.client = client
        self.test_items = {}
        self.update_test_items()

    def get_completions(self, document, complete_event):
        if '::' in document.text_before_cursor:
            path, pref = document.text_before_cursor.rsplit('::', 1)
            ns = self._module(path)
            if ns:
                for func in ns:
                    yield Completion(func, start_position=-len(pref))
        elif document.text_before_cursor.rfind(':') == len(document.text_before_cursor) - 1:
            if self._module(document.text_before_cursor[:-1]):  # check module existence
                yield Completion(':', start_position=0)  # ':' -> '::'
        else:  # module
            comps = document.text_before_cursor.rsplit('/', 1)
            ans = comps[:-1]
            if len(ans) > 0:
                ns = self._module('/'.join(ans))
                if ns:
                    for mod in ns:
                        yield Completion(mod, start_position=-len(comps[-1]))
            else:
                for mod in self.test_items:
                    yield Completion(mod, start_position=-document.cursor_position)

    def update_test_items(self):
        self.test_items = {}
        output = ''

        def output_hook(msg):
            nonlocal output
            msg_type = msg['header']['msg_type']
            content = msg['content']
            if msg_type in ('display_data', 'execute_result'):
                output = content['data'].get('text/plain', '')
            elif msg_type == 'error':
                print('\n'.join(content['traceback']), file=sys.stderr)
                sys.exit(1)

        self.client.execute_interactive(
            r"','.join({}.collect())".format(self.app_name),
            store_history=False,
            output_hook=output_hook
        )

        for nodeid in output[1:-1].split(','):
            path, func = nodeid.rsplit('::', 1)
            ns = self._module(path, create=True)
            ns[func] = True

    def _module(self, path, create=False):
        ns = self.test_items
        for mod in path.split('/'):
            if mod not in ns:
                if create:
                    ns[mod] = {}
                else:
                    return None
            ns = ns[mod]
        return ns


class PyTestLexer(Lexer):

    def lex_document(self, cli, document):
        lines = document.lines

        def get_line(lineno):
            try:
                line = lines[lineno]
                if '::' in line:
                    path, func = line.rsplit('::', 1)
                    return self._mod_tokens(path) + self._func_tokens(func)
                else:
                    return self._mod_tokens(line)

            except IndexError:
                return []

        return get_line

    def _mod_tokens(self, path):
        return [n for m in path.split('/')
                for n in [(Token.Name.Namespace, m), (Token.Name.Other, '/')]][:-1]

    def _func_tokens(self, func):
        return [(Token.Name.Other, '::'), (Token.Name.Function, func)]


class PyTestRunnerApp(BaseTurretApp):

    completer_class = PyTestCompleter

    lexer_class = PyTestLexer

    def __init__(self, app_name, turret_conf, turret_port, turret_status,
                 args=['-s', '-v'], plugins=[], auto_test=[], auto_test_map={},
                 uncache=[]):
        super().__init__(app_name, turret_conf, turret_port, turret_status)

        self.args = args
        self.plugins = plugins
        self.auto_test = auto_test
        self.auto_test_map = auto_test_map
        self.uncache = uncache or find_packages()

        # Suppress pytest warning for plugin: 'Module already imported'
        for plugin in pkg_resources.iter_entry_points('pytest11'):
            mod = import_module(plugin.module_name.split('.')[0])
            mod.__doc__ = 'PYTEST_DONT_REWRITE'

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

    @capture_method_output
    def collect(self):
        test_collector = TestCollector()
        pytest.main(['-qq', '--collect-only'], plugins=[test_collector])
        return test_collector.test_items

    @classmethod
    def command_to_code(self, app_name, command):
        return '{}.test({!r})'.format(app_name, command)
