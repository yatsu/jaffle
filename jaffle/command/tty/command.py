# -*- coding: utf-8 -*-

import io
import pexpect
import re
import sys
from ..base import BaseJaffleCommand


class OutputStream(io.StringIO):
    """
    Output stream for JaffleTTYCommand which drops escape sequences.
    """

    _ESC_PATTERN = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-ln-~]')
    _ESC_PATTERN_NOCOLOR = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')

    def __init__(self, color=True):
        """
        Initializes OutputStream.

        Parameters
        ----------
        color : bool
            Whether to enable color output.
        """
        super().__init__()

        self.color = color

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
        if self.color:
            return self._ESC_PATTERN.sub('', buf)
        else:
            return self._ESC_PATTERN_NOCOLOR.sub('', buf)

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


class JaffleTTYCommand(BaseJaffleCommand):
    """
    Process executor with TTY support.
    """
    description = __doc__

    examples = '''
jaffle tty "yarn test"
    '''

    def parse_command_line(self, argv):
        """
        Parses comnand line.

        Parameters
        ----------
        argv : list[str]
            Command line strings.
        """
        super().parse_command_line(argv)

        self.command = ' '.join(self.extra_args)

    def start(self):
        """
        Starts the session and attaches the shell to the app.
        """
        proc = pexpect.spawn(self.command, encoding='utf-8')
        proc.logfile = OutputStream(self.color)
        proc.expect(pexpect.EOF, timeout=None)
