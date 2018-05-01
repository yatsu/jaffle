# -*- coding: utf-8 -*-

# Install the pyzmq ioloop. This has to be done before anything else from
# tornado is imported.
from zmq.eventloop import ioloop
ioloop.install()

from jupyter_core.paths import SYSTEM_JUPYTER_PATH  # noqa
from pathlib import Path  # noqa
from .base import BaseJaffleCommand  # noqa
from .start import JaffleStartCommand  # noqa
from .console import JaffleConsoleCommand  # noqa
from .attach import JaffleAttachCommand  # noqa
from .tty import JaffleTTYCommand  # noqa


class JaffleMainCommand(BaseJaffleCommand):
    """
    Jaffle main command.
    """
    description = __doc__

    subcommands = dict(
        start=(JaffleStartCommand, JaffleStartCommand.description.splitlines()[0]),
        console=(JaffleConsoleCommand, JaffleConsoleCommand.description.splitlines()[0]),
        attach=(JaffleAttachCommand, JaffleAttachCommand.description.splitlines()[0]),
        tty=(JaffleTTYCommand, JaffleTTYCommand.description.splitlines()[0])
    )


SYSTEM_JUPYTER_PATH.insert(0, str(Path(__file__).parent.parent / 'data'))


main = launch_new_instance = JaffleMainCommand.launch_instance
