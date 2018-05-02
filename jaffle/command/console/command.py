# -*- coding: utf-8 -*-

from jupyter_client.consoleapp import JupyterConsoleApp
from jupyter_console.app import ZMQTerminalIPythonApp
from pathlib import Path
import signal
import sys
from ..base import BaseJaffleCommand
from ...shell import JaffleInteractiveShell
from ...status import JaffleStatus


class JaffleConsoleCommand(BaseJaffleCommand, ZMQTerminalIPythonApp):
    """
    Console for a jaffle kernel.
    """
    description = __doc__

    examples = '''
jaffle console py_kernel
    '''

    aliases = BaseJaffleCommand.aliases
    flags = BaseJaffleCommand.flags
    frontend_aliases = set()
    frontend_flags = set()

    def parse_command_line(self, argv):
        """
        Parses comnand line.

        Parameters
        ----------
        argv : list[str]
            Command line strings.
        """
        BaseJaffleCommand.parse_command_line(self, argv)

        if not self.extra_args:
            print('No kernel specified.', file=sys.stderr)
            self.exit(1)

        self.session_id = self.extra_args[0]

        try:
            status = JaffleStatus.load(self.status_file_path)
            print('status', status)
        except FileNotFoundError:
            print('Jaffle is not running - runtime_dir: {}'
                  .format(Path(self.runtime_dir).relative_to(Path.cwd())),
                  file=sys.stderr)
            self.exit(1)

        try:
            kernel_id = status.sessions[self.session_id].kernel.id
            self.existing = str(self.kernel_connection_file_path(kernel_id))

        except KeyError:
            print('Kernel {!r} is not running'.format(kernel_id), file=sys.stderr)
            self.exit(1)

    def init_shell(self):
        """
        Initializes the interactive shell and set signal handlers.
        """
        # Initializes kernel client and ZeroMQ channels.
        JupyterConsoleApp.initialize(self)

        signal.signal(signal.SIGINT, self.handle_sigint)
        self.shell = JaffleInteractiveShell.instance(
            parent=self,
            manager=self.kernel_manager,
            client=self.kernel_client,
        )
        self.shell.own_kernel = not self.existing

        _ask_exit_org = self.shell.ask_exit

        def ask_exit():
            print('Detaching {}'.format(self.session_id))
            _ask_exit_org()

        self.shell.ask_exit = ask_exit
