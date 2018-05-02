# -*- coding: utf-8 -*-

# Install the pyzmq ioloop. This has to be done before anything else from
# tornado is imported.
from zmq.eventloop import ioloop
ioloop.install()

from jupyter_core.paths import SYSTEM_JUPYTER_PATH  # noqa
from pathlib import Path  # noqa
from .main import JaffleMainCommand  # noqa


SYSTEM_JUPYTER_PATH.insert(0, str(Path(__file__).parent.parent / 'data'))


main = launch_new_instance = JaffleMainCommand.launch_instance
