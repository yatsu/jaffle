# -*- coding: utf-8 -*-

from jupyter_client.consoleapp import JupyterConsoleApp
import signal
import sys
from traitlets.config import catch_config_error
from ...status import TurretStatus
from ..base import BaseTurretCommand
from .shell import TurretAppShell


class TurretAttachCommand(BaseTurretCommand, JupyterConsoleApp):
    """
    Attach to a turret app.
    """
    description = __doc__

    examples = '''
turret attach pytest
    '''

    classes = [TurretAppShell] + JupyterConsoleApp.classes

    aliases = BaseTurretCommand.aliases
    flags = BaseTurretCommand.flags
    frontend_aliases = set()
    frontend_flags = set()

    _data_dir_default = BaseTurretCommand._data_dir_default
    _runtime_dir_default = BaseTurretCommand._runtime_dir_default

    def parse_command_line(self, argv):
        """
        Parses comnand line.

        Parameters
        ----------
        argv : list[str]
            Command line strings.
        """
        BaseTurretCommand.parse_command_line(self, argv)

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
        """
        Initializes TurretServer.
        Setup Jupyter and Turret managers before starting the server.

        Parameters
        ----------
        argv : list[str]
            Command line strings.
        """
        super().initialize(argv)

        self._dispatching = False

        self.init_shell()

    def init_shell(self):
        """
        Initializes the interactive shell and set signal handlers.
        """
        JupyterConsoleApp.initialize(self)

        signal.signal(signal.SIGINT, self._handle_sigint)
        self.shell = TurretAppShell.instance(
            parent=self, manager=self.kernel_manager, client=self.kernel_client,
            app_name=self.app.name, app_conf=self.app_conf
        )

    def start(self):
        """
        Starts the session and attaches the shell to the app.
        """
        self.log.info('Attaching %s', self.app_name)
        self.shell.mainloop()

    def _handle_sigint(self, sig, frame):
        """
        SIGINT handler.

        Parameters
        ----------
        sig : int
            Signal number.
        frame: frame
            Interrupted stack frame.
        """
        if self.shell._executing:
            self.kernel_manager.interrupt_kernel()
        else:
            raise KeyboardInterrupt
