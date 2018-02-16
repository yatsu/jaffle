# -*- coding: utf-8 -*-

from jupyter_console.app import ZMQTerminalIPythonApp
import sys
from .base import TurretBaseCommand


class TurretAttachCommand(ZMQTerminalIPythonApp, TurretBaseCommand):
    """
    Attach to a turret app.
    """
    description = __doc__

    examples = '''
turret attach main
turret attach test
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

        kernel_id = self.kernel_id = self.extra_args[0]

        try:
            sessions = self.read_sessions_file()
        except FileNotFoundError:
            print('Turret is not running.', file=sys.stderr)
            self.exit(1)

        try:
            kernel_id = sessions[kernel_id]['kernel']['id']
            self.existing = str(self.kernel_connection_file(kernel_id))

        except KeyError:
            print('Kernel {!r} is not running'.format(kernel_id), file=sys.stderr)
            self.exit(1)

    def init_shell(self):
        super().init_shell()

        _ask_exit_org = self.shell.ask_exit

        def ask_exit():
            print('Detaching {}'.format(self.kernel_id))
            _ask_exit_org()

        self.shell.ask_exit = ask_exit
