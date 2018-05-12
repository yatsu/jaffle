# -*- coding: utf-8 -*-

from jupyter_client.channels import HBChannel
from jupyter_client.threaded import ThreadedKernelClient
from unittest.mock import call, patch, Mock
from jaffle.kernel_client import JaffleZMQSocketChannel, JaffleIOPubChannel, JaffleKernelClient


def test_zmq_socket_channel():
    socket = Mock()
    session = Mock()
    io_loop = Mock()

    with patch('jupyter_client.threaded.Event'):
        channel = JaffleZMQSocketChannel(socket, session, io_loop)

    assert channel._handlers == {}

    handler = Mock()
    channel.add_handler(handler)

    assert channel._handlers == {id(handler): handler}

    msg = Mock()
    channel.call_handlers(msg)

    io_loop.add_callback.assert_called_with(handler, msg)

    channel.remove_handler(handler)

    assert channel._handlers == {}


def test_iopub_channel():
    socket = Mock()
    session = Mock()
    io_loop = Mock()

    with patch('jaffle.kernel_client.logger') as logger:
        with patch('jupyter_client.threaded.Event'):
            with patch('jaffle.kernel_client.JaffleZMQSocketChannel.call_handlers') \
                  as call_handlers:
                channel = JaffleIOPubChannel(socket, session, io_loop)
                channel.call_handlers({'msg_type': 'unknown'})
                channel.call_handlers({
                    'msg_type': 'error',
                    'content': {
                        'traceback': [
                            '----',
                            '  Foo',
                        ]
                    }
                })
                channel.call_handlers({
                    'msg_type': 'error',
                    'content': {
                        'traceback': [
                            'Bar',
                            'Baz  '
                        ]
                    }
                })
                channel.call_handlers({
                    'msg_type': 'stream',
                    'content': {
                        'name': 'stderr',
                        'text': 'Hello'
                    }
                })

    logger.error.assert_has_calls([
        call('Foo'),
        call('Bar\nBaz')
    ])

    logger.warning.assert_called_once_with('Hello')

    call_handlers.assert_has_calls([
        call({'msg_type': 'unknown'})
    ])


def test_kernel_client():
    assert issubclass(JaffleKernelClient, ThreadedKernelClient)
    assert JaffleKernelClient.iopub_channel_class.klass is JaffleIOPubChannel
    assert JaffleKernelClient.shell_channel_class.klass is JaffleZMQSocketChannel
    assert JaffleKernelClient.stdin_channel_class.klass is JaffleZMQSocketChannel
    assert JaffleKernelClient.hb_channel_class.klass is HBChannel
