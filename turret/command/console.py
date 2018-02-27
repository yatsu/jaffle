# -*- coding: utf-8 -*-

from jupyter_client.consoleapp import JupyterConsoleApp
from jupyter_console.app import ZMQTerminalIPythonApp
import signal
import sys
from .base import TurretBaseCommand
from ..shell import TurretInteractiveShell
from ..status import TurretStatus


class TurretConsoleCommand(TurretBaseCommand, ZMQTerminalIPythonApp):
    """
    Console for a turret kernel.
    """
    description = __doc__

    examples = '''
turret console py_kernel
    '''

    aliases = TurretBaseCommand.aliases
    flags = TurretBaseCommand.flags
    frontend_aliases = set()
    frontend_flags = set()

    _data_dir_default = TurretBaseCommand._data_dir_default
    _runtime_dir_default = TurretBaseCommand._runtime_dir_default

    def parse_command_line(self, argv):
        TurretBaseCommand.parse_command_line(self, argv)

        if not self.extra_args:
            print('No kernel specified.', file=sys.stderr)
            self.exit(1)

        self.session_id = self.extra_args[0]

        try:
            status = TurretStatus.load(self.status_file_path)
        except FileNotFoundError:
            print('Turret is not running.', file=sys.stderr)
            self.exit(1)

        try:
            kernel_id = status.sessions[self.session_id].kernel.id
            self.existing = str(self.kernel_connection_file_path(kernel_id))

        except KeyError:
            print('Kernel {!r} is not running'.format(kernel_id), file=sys.stderr)
            self.exit(1)

    def init_shell(self):
        JupyterConsoleApp.initialize(self)

        signal.signal(signal.SIGINT, self.handle_sigint)
        self.shell = TurretInteractiveShell.instance(
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
