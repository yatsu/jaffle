# -*- coding: utf-8 -*-

import io
import pexpect
import re
import sys
from .base import BaseTurretCommand


class OutputStream(io.StringIO):
    """
    Output stream for TurretTTYCommand which drops escape sequences.
    """

    _ESC_PATTERN = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-ln-~]')

    def _drop_escape_sequences(self, buf):
        """
        Drops escape sequences from the string except for ANSI colors.

        Parameters
        ----------
        buf : str
            Target string.

        Returns
        -------
        buf : str
            Result string.
        """
        return self._ESC_PATTERN.sub('', buf)

    def write(self, buf):
        """
        Writes to the stream.

        Parameters
        ----------
        buf : str
            String buffer to be written.
        """
        sys.stdout.write(self._drop_escape_sequences(buf))

    def flush(self):
        """
        Flushes the stream.
        """
        sys.stdout.flush()


class TurretTTYCommand(BaseTurretCommand):
    """
    Process executor with TTY support.
    """
    description = __doc__

    examples = '''
turret tty yarn test
    '''

    def parse_command_line(self, argv):
        """
        Parses comnand line.

        Parameters
        ----------
        argv : list[str]
            Command line strings.
        """
        self.args = argv

    def start(self):
        """
        Starts the session and attaches the shell to the app.
        """
        proc = pexpect.spawn(' '.join(self.args), encoding='utf-8')
        proc.logfile = OutputStream()
        proc.expect(pexpect.EOF, timeout=None)
