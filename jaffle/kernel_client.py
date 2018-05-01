# -*- coding: utf-8 -*-

from jupyter_client.channels import HBChannel
from jupyter_client.threaded import ThreadedZMQSocketChannel, ThreadedKernelClient
import logging
from traitlets import Type


logger = logging.getLogger('jaffle')


class JaffleZMQSocketChannel(ThreadedZMQSocketChannel):
    """
    ThreadedZMQSocketChannel for Jaffle which calls callbacks in an ioloop.
    """
    def __init__(self, socket, session, loop):
        """
        Initializes JaffleZMQSocketChannel.

        Parameters
        ----------
        socket : :class:`zmq.Socket`
            The ZMQ socket to use.
        session : :class:`session.Session`
            The session to use.
        loop
            A pyzmq ioloop to connect the socket to using a ZMQStream
        callback : function

        """
        super().__init__(socket, session, loop)

        self._handlers = {}

    def call_handlers(self, msg):
        """
        Call message handlers.

        Parameters
        ----------
        msg : dict
            ZeroMQ message.
        """
        for handler in self._handlers.values():
            self.ioloop.add_callback(handler, msg)

    def add_handler(self, handler):
        """
        Adds a channel message handler to the channel.

        Parameters
        ----------
        handler : function
            Channel message handler.
        """
        self._handlers[id(handler)] = handler

    def remove_handler(self, handler):
        """
        Removes the given channel message handler.

        Parameters
        ----------
        handler : function
            Channel message handler.
        """
        if id(handler) in self._handlers:
            del self._handlers[id(handler)]


class JaffleIOPubChannel(JaffleZMQSocketChannel):
    """
    Socket channel to receive messages from IOPub.
    This is required for error logging in the Jaffle server.
    """

    def call_handlers(self, msg):
        """
        Call message handlers for IOPub message.
        If ``msg_type`` is 'error', sends the traceback to the Jaffle main
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


class JaffleKernelClient(ThreadedKernelClient):
    """
    Jupyter kernel client for Jaffle server.

    It has a custom IOPub channel for error logging.
    """

    iopub_channel_class = Type(JaffleIOPubChannel)
    shell_channel_class = Type(JaffleZMQSocketChannel)
    stdin_channel_class = Type(JaffleZMQSocketChannel)
    hb_channel_class = Type(HBChannel)
