# -*- coding: utf-8 -*-

# Install the pyzmq ioloop. This has to be done before anything else from
# tornado is imported.
from zmq.eventloop import ioloop
ioloop.install()

from jupyter_core.paths import SYSTEM_JUPYTER_PATH  # noqa
from pathlib import Path  # noqa
from .base import BaseTurretCommand  # noqa
from .start import TurretStartCommand  # noqa
from .console import TurretConsoleCommand  # noqa
from .attach import TurretAttachCommand  # noqa
from .tty import TurretTTYCommand  # noqa


class TurretMainCommand(BaseTurretCommand):
    """
    Turret main command.
    """
    description = __doc__

    subcommands = dict(
        start=(TurretStartCommand, TurretStartCommand.description.splitlines()[0]),
        console=(TurretConsoleCommand, TurretConsoleCommand.description.splitlines()[0]),
        attach=(TurretAttachCommand, TurretAttachCommand.description.splitlines()[0]),
        tty=(TurretTTYCommand, TurretTTYCommand.description.splitlines()[0])
    )


SYSTEM_JUPYTER_PATH.insert(0, str(Path(__file__).parent.parent / 'data'))


main = launch_new_instance = TurretMainCommand.launch_instance
