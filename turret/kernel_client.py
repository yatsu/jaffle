# -*- coding: utf-8 -*-

from jupyter_client.blocking import BlockingKernelClient
from jupyter_client.blocking.channels import ZMQSocketChannel
import logging
from traitlets import Type
from zmq.eventloop import zmqstream

logger = logging.getLogger('turret')


class TurretIOPubChannel(ZMQSocketChannel):
    """
    Socket channel to receive messages from IOPub.
    This is required for error logging in the Turret server.
    """

    def __init__(self, socket, session, loop=None):
        """
        Initializes TurretIOPubChannel.
        Sets a message handler to IOPub.

        Parameters
        ----------
        socket : :class:`zmq.Socket`
            The ZMQ socket to use.
        session : :class:`session.Session`
            The session to use.
        loop
            Unused here, for other implementations.
        """
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
        """
        Message handlers for IOPub.
        If ``msg_type`` is 'error', sends the traceback to the Turret main
        logger.

        Parameters
        ----------
        msg : dict
            IOPub message.
        """
        if msg['msg_type'] == 'error':
            traceback = msg['content']['traceback']
            if '----' in traceback[0]:  # ignore the separator line
                logger.error('\n'.join(traceback[1:]).strip())
            else:
                logger.error('\n'.join(traceback).strip())
        if msg['msg_type'] == 'stream':
            if msg['content']['name'] == 'stderr':
                logger.warning(msg['content']['text'])


class TurretKernelClient(BlockingKernelClient):
    """
    Jupyter kernel client for Turret server.

    It has a custom IOPub channel for error logging.
    """

    iopub_channel_class = Type(TurretIOPubChannel)
