# -*- coding: utf-8 -*-

from .base import BaseJaffleCommand
from .attach import JaffleAttachCommand  # noqa
from .console import JaffleConsoleCommand  # noqa
from .start import JaffleStartCommand  # noqa
from .stop import JaffleStopCommand  # noqa
from .tty import JaffleTTYCommand  # noqa


class JaffleMainCommand(BaseJaffleCommand):
    """
    Jaffle main command.
    """
    description = __doc__

    subcommands = dict(
        start=(JaffleStartCommand, JaffleStartCommand.description.splitlines()[0]),
        stop=(JaffleStopCommand, JaffleStopCommand.description.splitlines()[0]),
        console=(JaffleConsoleCommand, JaffleConsoleCommand.description.splitlines()[0]),
        attach=(JaffleAttachCommand, JaffleAttachCommand.description.splitlines()[0]),
        tty=(JaffleTTYCommand, JaffleTTYCommand.description.splitlines()[0])
    )
