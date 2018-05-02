# -*- coding: utf-8 -*-

import os
from pathlib import Path
import signal
import sys
from ...status import JaffleStatus
from ..base import BaseJaffleCommand


class JaffleStopCommand(BaseJaffleCommand):
    """
    Stops Jaffle server.
    """

    description = __doc__

    exmaples = '''
jaffle stop
    '''

    aliases = {
        'runtime-dir': 'BaseJaffleCommand.runtime_dir'
    }
    flags = {}

    def start(self):
        """
        Executes the stop command.
        """
        try:
            status = JaffleStatus.load(self.status_file_path)
            print('Terminating process: {}'.format(status.pid))
            os.kill(status.pid, signal.SIGTERM)

        except FileNotFoundError:
            print('Jaffle is not running - runtime_dir: {}' .format(self.runtime_dir),
                  file=sys.stderr)
            self._cleanup_runtime_dir()
            self.exit(1)

        except ProcessLookupError:
            print('Jaffle has already stopped')
            self._cleanup_runtime_dir()
            self.exit(1)

    def _cleanup_runtime_dir(self):
        """
        Cleans up the runtime directory.
        """
        runtime_dir = Path(self.runtime_dir)
        print('Cleaning up the runtime directory: {}'.format(self.runtime_dir))
        self._unlink(runtime_dir / 'jaffle.json')
        self._unlink(runtime_dir / 'jaffle.json.lock')
        for conn_file in runtime_dir.glob('kernel-*.json'):
            self._unlink(conn_file)

    def _unlink(self, file_path):
        """
        Unlinks a file without raising ``FileNotFoundError``.

        Parameters
        ----------
        file_path : pathlib.Path
            File path.
        """
        try:
            file_path.unlink()
        except FileNotFoundError:
            pass
