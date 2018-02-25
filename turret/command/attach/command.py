# -*- coding: utf-8 -*-

from jupyter_client.consoleapp import JupyterConsoleApp
import signal
import sys
from traitlets.config import catch_config_error
from ...status import TurretStatus
from ..base import TurretBaseCommand
from .shell import TurretAppShell


class TurretAttachCommand(TurretBaseCommand, JupyterConsoleApp):
    """
    Attach to a turret app.
    """
    description = __doc__

    examples = '''
turret attach pytest_runner
    '''

    classes = [TurretAppShell] + JupyterConsoleApp.classes

    aliases = TurretBaseCommand.aliases
    flags = TurretBaseCommand.flags
    frontend_aliases = set()
    frontend_flags = set()

    _data_dir_default = TurretBaseCommand._data_dir_default
    _runtime_dir_default = TurretBaseCommand._runtime_dir_default

    def parse_command_line(self, argv):
        TurretBaseCommand.parse_command_line(self, argv)

        if not self.extra_args:
            print('No app specified.', file=sys.stderr)
            self.exit(1)

        self.app_name = self.extra_args[0]

        try:
            self.status = TurretStatus.load(self.status_file_path)
        except FileNotFoundError:
            print('Turret is not running.', file=sys.stderr)
            self.exit(1)

        try:
            self.app = self.status.apps[self.app_name]
            self.app_conf = self.status.conf['app'][self.app_name]

        except KeyError:
            print('App {!r} is not running'.format(self.app_name), file=sys.stderr)
            self.exit(1)

        kernel_id = self.status.sessions[self.app.session_name].kernel.id
        self.existing = str(self.kernel_connection_file_path(kernel_id))

    @catch_config_error
    def initialize(self, argv=None):
        super().initialize(argv)

        self._dispatching = False

        self.init_shell()

    def init_shell(self):
        JupyterConsoleApp.initialize(self)

        signal.signal(signal.SIGINT, self.handle_sigint)
        self.shell = TurretAppShell.instance(
            parent=self, manager=self.kernel_manager, client=self.kernel_client,
            app_name=self.app.name, app_conf=self.app_conf
        )

    def start(self):
        self.log.info('Attaching %s', self.app_name)
        self.shell.mainloop()

    def handle_sigint(self, *args):
        if self.shell._executing:
            self.kernel_manager.interrupt_kernel()
        else:
            raise KeyboardInterrupt
