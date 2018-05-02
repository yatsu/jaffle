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
            print('Jaffle is not running - runtime_dir: {}'
                  .format(Path(self.runtime_dir).relative_to(Path.cwd())),
                  file=sys.stderr)
            self.exit(1)

        except ProcessLookupError:
            runtime_dir = Path(self.runtime_dir)
            print('Jaffle has already stopped')
            print('Cleaning up the runtime directory: {}'
                  .format(runtime_dir.relative_to(Path.cwd())))
            try:
                (runtime_dir / 'jaffle.json').unlink()
                (runtime_dir / 'jaffle.json.lock').unlink()
                for conn_file in runtime_dir.glob('kernel-*.json'):
                    try:
                        conn_file.unlink()
                    except FileNotFoundError:
                        pass
            except FileNotFoundError:
                pass
