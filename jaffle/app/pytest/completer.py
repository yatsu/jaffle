# -*- coding: utf-8 -*-

from prompt_toolkit.completion import Completer, Completion
import sys


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
            r"','.join({}.collect_test_items())".format(self.app_name),
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
