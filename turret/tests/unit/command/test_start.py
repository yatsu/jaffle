# -*- coding: utf-8 -*-

import logging
from notebook.services.kernels.kernelmanager import MappingKernelManager
from pathlib import Path
import pytest
import signal
from tornado import gen, ioloop
from unittest.mock import call, mock_open, patch, Mock
import zmq
from zmq.eventloop import zmqstream
from turret.command.start import TurretStartCommand
from turret.process import Process
from turret.session import TurretSessionManager
from turret.status import TurretStatus, TurretSession


@pytest.fixture(scope='function')
def command():
    command = TurretStartCommand()
    command.check_running = Mock()
    command.initialize(argv=[])
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
    assert command.conf_file == Path('turret.hcl')

    with patch.object(command, 'load_conf'):
        command.initialize(argv=['foo.hcl'])

    assert command.conf_file == Path('foo.hcl')


def test_initialize():
    command = TurretStartCommand()
    command.check_running = Mock()

    with patch('turret.command.start.TurretStatus',
               return_value=Mock(TurretStatus)) as status:
        with patch.object(command, 'init_dir') as init_dir:
            with patch.object(command, 'init_signal') as init_signal:
                with patch.object(command, 'load_conf') as load_conf:
                    command.initialize(argv=[])

    command.check_running.assert_called_once_with()
    init_dir.assert_called_once_with()
    init_signal.assert_called_once_with()
    load_conf.assert_called_once_with()
    status.assert_called_once_with(conf={})

    with patch('turret.command.start.os.environ', {}) as environ:
        mock_dir = Mock(Path, return_value=Mock(exists=lambda: False))
        with patch('turret.command.start.Path', mock_dir) as path:
            command.init_dir()

    assert environ == {'JUPYTER_DATA_DIR': str(Path('.turret').absolute())}

    path.assert_has_calls([
        call(str(Path('.turret').absolute())),
        call(str((Path('.turret') / 'runtime').absolute()))
    ])

    mock_dir.return_value.mkdir.assert_has_calls([call(), call()])

    with patch('turret.command.start.sys.stdin.isatty', lambda: True):
        with patch('turret.command.start.signal.signal') as sig:
            command.init_signal()

    sig.assert_has_calls([
        call(signal.SIGINT, command._handle_sigint),
        call(signal.SIGTERM, command._signal_stop)
    ])

    mopen = mock_open(read_data='py_kernel = {}')
    with patch('turret.command.start.Path.open', mopen):
        command.load_conf()

    assert command.conf == {'py_kernel': {}}


def test_start(command):
    with patch('turret.command.start.ioloop.IOLoop.current',
               return_value=Mock(ioloop.IOLoop)) as ioloop_current:
        with patch('turret.command.start.zmq.Context.instance',
                   return_value=Mock(socket=Mock(return_value=Mock(
                       zmq.Socket,
                       bind_to_random_port=Mock(return_value=1234)
                   )))) as zmq_instance:
            with patch('turret.command.start.zmqstream.ZMQStream',
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

    zmq_stream.assert_called_once_with(command.socket)
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
        TurretSessionManager,
        list_sessions=Mock(return_value=[
            {'id': 'session-1', 'name': 'Session 1'},
            {'id': 'session-2', 'name': 'Session 2'}
        ]),
        delete_session=delete_session
    )
    command.status = Mock(
        TurretStatus,
        sessions={
            'turret-session-1': Mock(TurretSession, kernel=Mock(id='kernel-1')),
            'turret-session-2': Mock(TurretSession, kernel=Mock(id='kernel-2'))
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
def test_multiple_kernel_error(command):
    command.conf = {'kernel': {'foo': {}, 'bar': {}}}
    with pytest.raises(SystemExit) as ex:
        yield command._start_sessions()

    assert ex.type == SystemExit
    assert ex.value.code == 1

    assert (str(command.log.error.call_args[0][0]) ==
            'Turret currently supports only one kernel')


@pytest.mark.gen_test
def test_start_sessions(command):
    created_sessions = []

    def create_session(**kwargs):
        created_sessions.append(kwargs)
        future = gen.Future()
        future.set_result({'id': 'sess-id', 'kernel': 'sess_kernel'})
        return future

    command.conf = {
        'kernel': {
            'my_kernel_instance': {
                'kernel_name': 'my_kernel'
            }
        }
    }
    command.session_manager = Mock(TurretSessionManager, create_session=create_session)
    session = Mock(TurretSession, kernel=Mock(id='kernel-1'))
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
        TurretStatus,
        sessions={'my_kernel_instance': session},
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
    with patch('turret.command.start.logging.getLogger', return_value=logger) as get_logger:
        yield command._start_sessions()

    assert created_sessions == [{
        'name': 'my_kernel_instance',
        'kernel_name': 'my_kernel',
        'env': {
            'PYTHONSTARTUP': str((Path(__file__).parent.parent.parent.parent / 'startup.py'))
        }
    }]

    command.status.add_session.assert_called_once_with(
        'sess-id', 'my_kernel_instance', 'sess_kernel'
    )

    command._get_apps_for_session.assert_called_once_with('sess_name')

    command.kernel_manager.get_kernel.assert_called_once_with('kernel-1')

    client.start_channels.assert_called_once_with()
    client.wait_for_ready.assert_called_once_with()

    get_logger.assert_has_calls([call(name) for name in apps.keys()])
    assert logger.parent is command.log
    logger.setLevel.assert_has_calls([call(logging.DEBUG), call(logging.DEBUG)])

    assert len(client.execute.call_args_list) == 2

    exec1 = client.execute.call_args_list[0]
    "from foo import Foo;" in exec1[0]
    "app1 = Foo('app1', " in exec1[0]
    "**{'opt1': True}" in exec1[0]
    "app1.start()" in exec1[0]
    assert exec1[1] == {'silent': True}

    exec2 = client.execute.call_args_list[1]
    "from bar import Bar;" in exec2[0]
    "app2 = Bar('app2', " in exec2[0]
    "**{}" in exec2[0]
    assert exec2[1] == {'silent': True}

    client.shell_channel.get_msg.assert_has_calls([
        call(block=True), call(block=True)
    ])

    command.status.add_app.assert_has_calls([
        call(name=name, session_name='sess_name')
        for name in apps.keys()
    ])

    command.status.save.assert_called_once_with(command.status_file_path)
