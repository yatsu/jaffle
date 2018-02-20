# -*- coding: utf-8 -*-

from jupyter_client.blocking import BlockingKernelClient
from jupyter_client.blocking.channels import ZMQSocketChannel
import logging
from traitlets import Type
from zmq.eventloop import zmqstream

logger = logging.getLogger('turret')


class TurretIOPubChannel(ZMQSocketChannel):

    def __init__(self, socket, session, loop=None):
        super().__init__(socket, session, loop=loop)
        zmqstream.ZMQStream(self.socket).on_recv(self._handle_recv)

    def _handle_recv(self, msg):
        """
        Callback for stream.on_recv.

        Unpacks message, and calls handlers with it.
        """
        ident, smsg = self.session.feed_identities(msg)
        msg = self.session.deserialize(smsg)
        self.call_handlers(msg)

    def call_handlers(self, msg):
        pass


class TurretKernelClient(BlockingKernelClient):

    iopub_channel_class = Type(TurretIOPubChannel)
