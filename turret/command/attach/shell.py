# -*- coding: utf-8 -*-

from importlib import import_module
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.shortcuts import create_prompt_application, create_eventloop, create_output
from prompt_toolkit.styles import PygmentsStyle
from pygments.styles import get_style_by_name
from pygments.token import Token
from traitlets import Dict, Instance, Unicode, Type
from ...shell import TurretInteractiveShell
from ...app.base import BaseTurretApp


class TurretAppShell(TurretInteractiveShell):
    pt_cli = None

    _executing = False
    _execution_state = ''
    _pending_clearoutput = False
    _eventloop = None

    confirm_exit = False

    app_class = Type(BaseTurretApp)
    app_name = Unicode()
    app_conf = Dict()

    _completer = None
    _lexer = None

    client = Instance('jupyter_client.KernelClient', allow_none=True)

    def _client_changed(self, name, old, new):
        self.session_id = new.session.session

    session_id = Unicode()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def init_completer(self):
        mod_name, cls_name = self.app_conf['class'].rsplit('.', 1)
        self.app_class = getattr(import_module(mod_name), cls_name)

        comp_cls = self.app_class.completer_class
        if comp_cls:
            self._completer = comp_cls(self.app_name, self.app_conf, self.client)

    def init_lexer(self):
        lexer_cls = self.app_class.lexer_class
        if lexer_cls:
            self._lexer = lexer_cls()

    def init_prompt_toolkit_cli(self):
        self.init_lexer()

        kbmanager = KeyBindingManager.for_prompt()
        style_overrides = {
            Token.Prompt: '#aaddaa',
            Token.OutPrompt: '#ddaaaa',
            Token.Name.Namespace: '#ddaadd',
            Token.Name.Function: '#aadddd',
        }
        style_cls = get_style_by_name('default')
        style = PygmentsStyle.from_defaults(pygments_style_cls=style_cls,
                                            style_dict=style_overrides)
        app = create_prompt_application(
            get_prompt_tokens=self.get_prompt_tokens,
            key_bindings_registry=kbmanager.registry,
            completer=self._completer,
            lexer=self._lexer,
            style=style,
        )

        self._eventloop = create_eventloop()
        self.pt_cli = CommandLineInterface(
            app,
            eventloop=self._eventloop,
            output=create_output(true_color=False),
        )

    def get_prompt_tokens(self, cli):
        return [
            (Token.Prompt, '>>> ')
        ]

    def get_out_prompt_tokens(self):
        return [
            (Token.OutPrompt, '<<< ')
        ]

    def run_cell(self, cell, store_history=True):
        code = self.app_class.command_to_code(self.app_name, cell)
        super().run_cell(code)
