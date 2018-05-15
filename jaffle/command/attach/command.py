# -*- coding: utf-8 -*-

from jupyter_client.consoleapp import JupyterConsoleApp
from pathlib import Path
import signal
import sys
from traitlets.config import catch_config_error
from ...status import JaffleStatus
from ..base import BaseJaffleCommand
from .shell import JaffleAppShell


class JaffleAttachCommand(BaseJaffleCommand, JupyterConsoleApp):
    """
    Attach to a jaffle app.
    """
    description = __doc__

    examples = '''
jaffle attach pytest
    '''

    classes = [JaffleAppShell] + JupyterConsoleApp.classes

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
            print('No app specified.', file=sys.stderr)
            self.exit(1)

        self.app_name = self.extra_args[0]

        try:
            self.status = JaffleStatus.load(self.status_file_path)
        except FileNotFoundError:
            print('Jaffle is not running - runtime_dir: {}'
                  .format(Path(self.runtime_dir).relative_to(Path.cwd())),
                  file=sys.stderr)
            self.exit(1)

        try:
            self.app = self.status.apps[self.app_name]

        except KeyError:
            print('App {!r} is not running'.format(self.app_name), file=sys.stderr)
            self.exit(1)

        kernel_id = self.status.sessions[self.app.session_name].kernel.id
        self.existing = str(self.kernel_connection_file_path(kernel_id))

    @catch_config_error
    def initialize(self, argv=None):
        """
        Initializes JaffleAttachCommand.
        Setup Jupyter and Jaffle managers before starting the server.

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
        self.shell = JaffleAppShell.instance(
            parent=self, manager=self.kernel_manager, client=self.kernel_client,
            app_name=self.app.name, app_data=self.app
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
