# -*- coding: utf-8 -*-

from pathlib import Path
import signal
from turret.command.start import TurretStartCommand
from unittest.mock import call, mock_open, patch, Mock


def test_log_format_default():
    command = TurretStartCommand()
    command.initialize(argv=[])

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


def test_extra_args():
    command = TurretStartCommand()
    command.initialize(argv=[])

    assert command.conf_file == Path('turret.hcl')

    with patch.object(command, 'load_conf'):
        command.initialize(argv=['foo.hcl'])

    assert command.conf_file == Path('foo.hcl')


def test_initialize():
    command = TurretStartCommand()

    with patch.object(command, 'init_dir') as init_dir:
        with patch.object(command, 'init_signal') as init_signal:
            with patch.object(command, 'load_conf') as load_conf:
                with patch('turret.command.start.TurretStatus') as status:
                    command.initialize(argv=[])

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
