# -*- coding: utf-8 -*-

import logging
from notebook.services.kernels.kernelmanager import MappingKernelManager
from pathlib import Path
import pytest
import signal
from tornado import gen, ioloop
from unittest.mock import call, patch, Mock
import zmq
from zmq.eventloop import zmqstream
from jaffle.command.start import JaffleStartCommand
from jaffle.config import JaffleConfig, ConfigValue
from jaffle.process import Process
from jaffle.session import JaffleSessionManager
from jaffle.status import JaffleStatus, JaffleSession


@pytest.fixture(scope='function')
def command():
    command = JaffleStartCommand()
    command.check_running = Mock()
    command.initialize(argv=[])
    command._init_job_loggers = Mock()
    command.log = Mock(logging.Logger)
    return command


def test_log_format_default(command):
    log_format = command.log_format

    assert '%(time_color)' in log_format
    assert '%(time_color_end)' in log_format

    assert '%(name_color)' in log_format
    assert '%(name_color_end)' in log_format

    assert '%(level_color)' in log_format
    assert '%(level_color_end)' in log_format

    assert '%(asctime)' in log_format
    assert '%(msecs)' in log_format

    assert '%(name)' in log_format
    assert '%(message)' in log_format


def test_extra_args(command):
    assert command.conf_files == [Path('jaffle.hcl')]

    with patch('jaffle.command.start.command.Path.exists', return_value=True):
        with patch.object(command, 'load_conf'):
            command.initialize(argv=['jaffle.hcl', 'foo.hcl'])

    assert command.conf_files == [Path('jaffle.hcl'), Path('foo.hcl')]


def test_initialize():
    command = JaffleStartCommand()
    command.check_running = Mock()

    with patch.object(command, 'init_dir') as init_dir:
        with patch.object(command, 'init_signal') as init_signal:
            with patch.object(command, 'load_conf') as load_conf:
                command.initialize(argv=[])

    command.check_running.assert_called_once_with()
    init_dir.assert_called_once_with()
    init_signal.assert_called_once_with()
    load_conf.assert_called_once_with()

    with patch('jaffle.command.start.command.os.environ', {}) as environ:
        mock_dir = Mock(Path, return_value=Mock(exists=lambda: False))
        with patch('jaffle.command.start.command.Path', mock_dir) as path:
            command.init_dir()

    assert environ == {'JUPYTER_DATA_DIR': '.jaffle'}

    path.assert_has_calls([call('.jaffle')])

    mock_dir.return_value.mkdir.assert_has_calls([call()])

    with patch('jaffle.command.start.command.sys.stdin.isatty', lambda: True):
        with patch('jaffle.command.start.command.signal.signal') as sig:
            command.init_signal()

    sig.assert_has_calls([
        call(signal.SIGINT, command._handle_sigint),
        call(signal.SIGTERM, command._signal_stop)
    ])


def test_start(command):
    with patch('jaffle.command.start.command.ioloop.IOLoop.current',
               return_value=Mock(ioloop.IOLoop)) as ioloop_current:
        with patch('jaffle.command.start.command.zmq.Context.instance',
                   return_value=Mock(socket=Mock(return_value=Mock(
                       zmq.Socket,
                       bind_to_random_port=Mock(return_value=1234)
                   )))) as zmq_instance:
            with patch('jaffle.command.start.command.zmqstream.ZMQStream',
                       return_value=Mock(zmqstream.ZMQStream)) as zmq_stream:
                command.start()

    ioloop_current.assert_called_once_with()

    ioloop_current.return_value.add_callback.assert_has_calls([
        call(command._start_sessions),
        call(command._start_processes)
    ])

    zmq_instance.return_value.socket.assert_called_once_with(zmq.PULL)
    assert command.socket is zmq_instance.return_value.socket.return_value

    command.socket.bind_to_random_port.assert_called_once_with(
        'tcp://*', min_port=9000, max_port=9099
    )
    assert command.port is command.socket.bind_to_random_port.return_value

    zmq_stream.assert_called_once_with(command.socket, command.io_loop)
    zmq_stream.return_value.on_recv.assert_called_once_with(command._on_recv_msg)

    ioloop_current.return_value.start.assert_called_once_with()


@pytest.mark.gen_test
def test_shutdown(command):
    deleted_sessions = []

    def delete_session(sess_id):
        deleted_sessions.append(sess_id)
        future = gen.Future()
        future.set_result(sess_id)
        return future

    command.socket = Mock(zmq.Socket)
    command.clients = {
        'client-1': Mock(),
        'client-2': Mock()
    }
    command.session_manager = Mock(
        JaffleSessionManager,
        list_sessions=Mock(return_value=[
            {'id': 'session-1', 'name': 'Session 1'},
            {'id': 'session-2', 'name': 'Session 2'}
        ]),
        delete_session=delete_session
    )
    command.status = Mock(
        JaffleStatus,
        sessions={
            'jaffle-session-1': Mock(JaffleSession, kernel=Mock(id='kernel-1')),
            'jaffle-session-2': Mock(JaffleSession, kernel=Mock(id='kernel-2'))
        }
    )
    command.kernel_connection_file_path = Mock(return_value=Mock())
    command.procs = {
        'proc-1': Mock(Process),
        'proc-2': Mock(Process)
    }
    command.io_loop = Mock(ioloop.IOLoop)

    yield command.shutdown()

    command.socket.close.assert_called_once_with()

    command.clients['client-1'].stop_channels.assert_called_once_with()
    command.clients['client-2'].stop_channels.assert_called_once_with()

    assert deleted_sessions == ['session-1', 'session-2']

    command.kernel_connection_file_path.assert_has_calls([
        call(sess.kernel.id) for sess in command.status.sessions.values()
    ])
    command.kernel_connection_file_path.return_value.assert_has_calls([
        call.exists(), call.unlink(),
        call.exists(), call.unlink()
    ])

    command.procs['proc-1'].stop.assert_called_once_with()
    command.procs['proc-2'].stop.assert_called_once_with()

    command.status.destroy.assert_called_once_with(command.status_file_path)

    command.io_loop.stop.assert_called_once_with()


@pytest.mark.gen_test
def test_start_sessions(command):
    created_sessions = []

    def create_session(**kwargs):
        created_sessions.append(kwargs)
        future = gen.Future()
        future.set_result({'id': 'sess-id', 'kernel': 'sess_kernel'})
        return future

    namespace = {}

    command.conf = Mock(
        JaffleConfig,
        namespace=namespace,
        variable=ConfigValue.create({}, namespace),
        kernel=ConfigValue.create({'sess_name': {'kernel_name': 'my_kernel'}}, namespace),
        app=ConfigValue.create({}, namespace),
        process=ConfigValue.create({}, namespace),
        job=ConfigValue.create({}, namespace),
        logger=ConfigValue.create({}, namespace)
    )
    command.session_manager = Mock(JaffleSessionManager, create_session=create_session)
    session = Mock(JaffleSession, kernel=Mock(id='kernel-1'))
    session.name = 'sess_name'  # `name` must be set after Mock()
    apps = {
        'app1': {
            'class': 'foo.Foo',
            'options': {'opt1': True},
            'start': 'app1.start()'
        },
        'app2': {
            'class': 'bar.Bar'
        }
    }
    command.status = Mock(
        JaffleStatus,
        sessions={'sess_name': session},
        to_dict=Mock(return_value={
            'sessions': {},
            'apps': apps,
            'cond': {}
        })
    )
    command._get_apps_for_session = Mock(return_value=apps)
    client = Mock(
        shell_channel=Mock(get_msg=Mock(return_value={
            'content': {
                'status': 'ok'
            }
        }))
    )
    command.kernel_manager = Mock(
        MappingKernelManager,
        get_kernel=Mock(return_value=Mock(client=Mock(return_value=client)))
    )

    logger = Mock()
    with patch('jaffle.command.start.command.logging.getLogger',
               return_value=logger) as get_logger:
        yield command._start_sessions()

    assert created_sessions == [{
        'name': 'sess_name',
        'kernel_name': 'my_kernel',
        'env': {
            'PYTHONSTARTUP': str(
                Path(__file__).parent.parent.parent.parent.parent / 'startup.py'
            )
        }
    }]

    command.status.add_session.assert_called_once_with(
        'sess-id', 'sess_name', 'sess_kernel'
    )

    command._get_apps_for_session.assert_called_once_with('sess_name')

    command.kernel_manager.get_kernel.assert_called_once_with('kernel-1')

    client.start_channels.assert_called_once_with()

    get_logger.assert_has_calls([call(name) for name in apps.keys()])
    assert logger.parent is command.log
    logger.setLevel.assert_has_calls([call(logging.DEBUG), call(logging.DEBUG)])

    command.status.add_app.assert_any_call(
        'app1', 'sess_name', 'foo.Foo', 'app1.start()', {'opt1': True}
    )
    command.status.add_app.assert_any_call(
        'app2', 'sess_name', 'bar.Bar', None, {}
    )

    command.status.save.assert_called_once_with(command.status_file_path)

    assert len(client.execute.call_args_list) == 1

    exec_args = client.execute.call_args_list[0]
    "from foo import Foo" in exec_args[0]
    "app1 = Foo('app1', " in exec_args[0]
    "**{'opt1': True}" in exec_args[0]
    "app1.start()" in exec_args[0]
    "from bar import Bar" in exec_args[0]
    "app2 = Bar('app2', " in exec_args[0]
    "**{}" in exec_args[0]
    assert exec_args[1] == {'silent': True}
