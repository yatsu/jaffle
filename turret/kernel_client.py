# -*- coding: utf-8 -*-

from jupyter_client.channels import HBChannel
from jupyter_client.threaded import ThreadedZMQSocketChannel, ThreadedKernelClient
import logging
from tornado import gen
from traitlets import Type


logger = logging.getLogger('turret')


class TurretZMQSocketChannel(ThreadedZMQSocketChannel):
    """
    ThreadedZMQSocketChannel for Turret which calls callbacks in an ioloop.
    """

    on_recv = None

    def call_handlers(self, msg):
        """
        Call message handlers.

        Parameters
        ----------
        msg : dict
            ZeroMQ message.
        """
        if self.on_recv:
            self.ioloop.add_callback(gen.maybe_future(self.on_recv(msg)))


class TurretIOPubChannel(TurretZMQSocketChannel):
    """
    Socket channel to receive messages from IOPub.
    This is required for error logging in the Turret server.
    """

    def call_handlers(self, msg):
        """
        Call message handlers for IOPub message.
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

        super().call_handlers(msg)


class TurretKernelClient(ThreadedKernelClient):
    """
    Jupyter kernel client for Turret server.

    It has a custom IOPub channel for error logging.
    """

    iopub_channel_class = Type(TurretIOPubChannel)
    shell_channel_clsss = Type(TurretZMQSocketChannel)
    stdin_channel_class = Type(TurretZMQSocketChannel)
    hb_channel_class = Type(HBChannel)
