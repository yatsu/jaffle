# -*- coding: utf-8 -*-

from prompt_toolkit import Application
from prompt_toolkit.buffer import AcceptAction, Buffer
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.document import Document
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.layout.containers import FloatContainer, HSplit, Window
from prompt_toolkit.layout.controls import FillControl
from prompt_toolkit.layout.dimension import LayoutDimension
from prompt_toolkit.shortcuts import create_asyncio_eventloop, create_output
from prompt_toolkit.styles import PygmentsStyle
from pygments.styles import get_style_by_name
from pygments.token import Token
from tornado import gen
from traitlets.config import SingletonConfigurable
from .controls import LogControl
from .containers import InputWindow


class JaffleMainShell(SingletonConfigurable):

    pt_cli = None
    confirm_exit = True
    shutdown = None

    _eventloop = None
    _keep_running = True

    def __init__(self, **kwargs):
        self.shutdown = kwargs.get('shutdown', lambda: None)
        self.document = Document('hello')
        self.init_pt_shell()

    def init_pt_shell(self):
        self._eventloop = create_asyncio_eventloop()

        self.pt_cli = CommandLineInterface(
            self._create_application(), eventloop=self._eventloop,
            output=create_output(true_color=True)
        )

    @gen.coroutine
    def mainloop(self):
        while True:
            try:
                yield self.interact()
                break
            except EOFError:
                self.log.debug('keyboard interrupt')
                if (not self.confirm_exit) \
                        or ask_yes_no('Do you really want to exit ([y]/n)?', 'y', 'n'):
                    self.stop_running()
                    self.shutdown()

        if self._eventloop:
            self._eventloop.close()

    @gen.coroutine
    def interact(self):
        while self._keep_running:
            command = yield self.prompt()
            if command:
                self.run_command(command)

    @gen.coroutine
    def prompt(self):
        with self.pt_cli.patch_stdout_context():
            document = yield self.pt_cli.run_async()
        return document.text if document else None

    def run_command(self, command):
        pass

    def stop_running(self):
        self._keep_running = False

    def _create_layout(self):
        return HSplit([
            FloatContainer(Window(LogControl(self.document)), floats=[]),
            Window(height=LayoutDimension.exact(1), content=FillControl('─', token=Token.Line)),
            InputWindow()
        ])

    def _create_buffer(self):
        history = InMemoryHistory()
        return Buffer(history=history, accept_action=AcceptAction.RETURN_DOCUMENT)

    def _create_kbmanager(self):
        kbmanager = KeyBindingManager.for_prompt()

        @kbmanager.registry.add_binding(Keys.ControlC, eager=True)
        def _ctrl_c(event):
            self.pt_cli.exit()

        return kbmanager

    def _create_style(self):
        style_overrides = {
            Token.Prompt: '#009900',
            Token.PromptNum: '#00ff00 bold',
            Token.OutPrompt: '#ff2200',
            Token.OutPromptNum: '#ff0000 bold'
        }
        style_cls = get_style_by_name('default')
        style_overrides.update({
            Token.Number: '#007700',
            Token.Operator: 'noinherit',
            Token.String: '#BB6622',
            Token.Name.Function: '#2080D0',
            Token.Name.Class: 'bold #2080D0',
            Token.Name.Namespace: 'bold #2080D0'
        })
        style = PygmentsStyle.from_defaults(pygments_style_cls=style_cls,
                                            style_dict=style_overrides)
        return style

    def _create_application(self):
        return Application(
            layout=self._create_layout(),
            buffer=self._create_buffer(),
            style=self._create_style(),
            key_bindings_registry=self._create_kbmanager().registry,
            use_alternate_screen=True,
            mouse_support=False,
            editing_mode=EditingMode.EMACS
        )


def ask_yes_no(prompt, default=None, interrupt=None):
    answers = {'y': True, 'n': False, 'yes': True, 'no': False}
    ans = None
    while ans not in answers.keys():
        try:
            ans = input(prompt + ' ').lower() or default
        except KeyboardInterrupt:
            if interrupt:
                ans = interrupt
        except EOFError:
            if default in answers.keys():
                ans = default
                print()
            else:
                raise

    return answers[ans]
