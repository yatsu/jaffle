# -*- coding: utf-8 -*-

from importlib import import_module
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.shortcuts import create_prompt_application, create_eventloop, create_output
from prompt_toolkit.styles import PygmentsStyle
from pygments.styles import get_style_by_name
from pygments.token import Token
from traitlets import Instance, Unicode, Type
from ...shell import JaffleInteractiveShell
from ...app.base import BaseJaffleApp


class JaffleAppShell(JaffleInteractiveShell):
    """
    Interactive shell for ``jaffle attach``.
    """

    pt_cli = None

    _executing = False
    _execution_state = ''
    _pending_clearoutput = False
    _eventloop = None

    confirm_exit = False

    app_class = Type(BaseJaffleApp)
    app_name = Unicode()
    app_data = Instance('jaffle.status.JaffleAppData')

    _completer = None
    _lexer = None

    client = Instance('jupyter_client.KernelClient', allow_none=True)

    def _client_changed(self, name, old, new):
        self.session_id = new.session.session

    session_id = Unicode()

    def init_completer(self):
        """
        Initializes the completer if it exists.
        """
        mod_name, cls_name = self.app_data.class_name.rsplit('.', 1)
        self.app_class = getattr(import_module(mod_name), cls_name)

        comp_cls = self.app_class.completer_class
        if comp_cls:
            self._completer = comp_cls(self.app_name, self.app_data, self.client)

    def init_lexer(self):
        """
        Initializes the lexer if it exists.
        """
        lexer_cls = self.app_class.lexer_class
        if lexer_cls:
            self._lexer = lexer_cls()

    def init_prompt_toolkit_cli(self):
        """
        Initializes the Prompt Tookkit CLI.
        """
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
        """
        Gets the prompt tokens.

        Parameters
        ----------
        cli : prompt_toolkit.interface.CommandLineInterface
            Prompt Toolkit CLI.

        Returns
        -------
        tokens : list[(pygments.token.Token, str)]
        """
        return [
            (Token.Prompt, '>>> ')
        ]

    def get_out_prompt_tokens(self):
        """
        Gets the output tokens.

        Returns
        -------
        tokens : list[(pygments.token.Token, str)]
        """
        return [
            (Token.OutPrompt, '<<< ')
        ]

    def run_cell(self, command, store_history=True):
        """
        Executes the command.

        Parameters
        ----------
        command : str
            The command to be executed.
        store_history : bool
            If True, the raw and translated cell will be stored in IPython's
            history. For user code calling back into IPython's machinery, this
            should be set to False.
        """
        code = self.app_class.command_to_code(self.app_name, command)
        super().run_cell(code)
