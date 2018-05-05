# -*- coding: utf-8 -*-

from notebook.utils import check_pid
import os
from pathlib import Path
import signal
import sys
import time
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
            print('Stopping Jaffle - PID: {}'.format(status.pid))
            os.kill(status.pid, signal.SIGTERM)

            for _ in range(50000):
                if check_pid(status. pid):
                    print("PID {} has finished".format(status.pid))
                    self._cleanup_runtime_dir(status)
                    sys.exit(0)
                time.sleep(0.1)

            os.kill(status.pid, signal.SIGKILL)

            for _ in range(50000):
                if check_pid(status. pid):
                    print("PID {} has finished".format(status.pid))
                    self._cleanup_runtime_dir(status)
                    sys.exit(0)
                time.sleep(0.1)

            print('Failed to stop Jaffle - PID: {}'.format(status.pid))

        except FileNotFoundError:
            print('Jaffle is not running - runtime_dir: {}' .format(self.runtime_dir),
                  file=sys.stderr)
            self.exit(1)

        except ProcessLookupError:
            print('Jaffle has already stopped')
            self._cleanup_runtime_dir(status)
            self.exit(1)

    def _cleanup_runtime_dir(self, status):
        """
        Cleans up the runtime directory.

        Parameters
        ----------
        status : JaffleStatus
            Jaffle server status.
        """
        runtime_dir = Path(self.runtime_dir)
        if not (runtime_dir / 'jaffle.json').exists():
            return
        print('Cleaning up the runtime directory: {}'.format(self.runtime_dir))
        try:
            for conn_file in runtime_dir.glob('kernel-*.json'):
                self._unlink(conn_file)
            status.destroy(runtime_dir / 'jaffle.json')
        except FileNotFoundError:
            pass

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
