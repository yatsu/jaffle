# -*- coding: utf-8 -*-

import sys
from .base import TurretBaseCommand


class TurretAttachCommand(TurretBaseCommand):
    """
    Attach to a turret app.
    """
    description = __doc__

    examples = '''
turret attach py_kernel
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
            print('No app specified.', file=sys.stderr)
            self.exit(1)

        self.app_name = self.extra_args[0]

    def start(self):
        self.log.info('Attaching %s', self.app_name)
