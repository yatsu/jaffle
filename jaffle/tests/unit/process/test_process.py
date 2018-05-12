# -*- coding: utf-8 -*-

import pytest
import signal
from subprocess import TimeoutExpired
from unittest.mock import call, patch, Mock
from jaffle.process.process import Process


def test_init():
    with patch('jaffle.process.process.ProcessLogger') as pl:
        log = Mock()
        proc = Process(log, 'foo', 'foo --help')

    assert proc.log is pl.return_value
    assert proc.proc_name == 'foo'
    assert proc.command == 'foo --help'
    assert proc.tty is False
    assert proc.env == {}
    assert proc.color is True

    pl.assert_called_once_with(log, [], [])

    with patch('jaffle.process.process.ProcessLogger') as pl:
        log = Mock()
        proc = Process(log, 'bar', 'bar --help', tty=True, env={'DEBUG': 'true'},
                       log_suppress_regex=['^test'],
                       log_replace_regex=[{'from': 'Hello, (.*)', 'to': '\\1'}],
                       color=False)

    assert proc.log is pl.return_value
    assert proc.proc_name == 'bar'
    assert proc.command == 'bar --help'
    assert proc.tty is True
    assert proc.env == {'DEBUG': 'true'}
    assert proc.color is False

    pl.assert_called_once_with(log, ['^test'], [{'from': 'Hello, (.*)', 'to': '\\1'}])


@pytest.mark.gen_test
def test_start(subprocess_mock):
    proc_log = Mock()
    with patch('jaffle.process.process.ProcessLogger', return_value=proc_log):
        with patch('jaffle.process.process.os') as os:
            os.environ = {'PATH': '/bin'}
            with patch('jaffle.process.process.Subprocess',
                       return_value=subprocess_mock) as subproc:
                proc = Process(Mock(), 'foo', 'foo --help', env={'BAR': 'bar'})
                yield proc.start()

    subproc.assert_called_once_with(
        ['foo', '--help'],
        env={'PATH': '/bin', 'BAR': 'bar'},
        stdin=None,
        stdout=subproc.STREAM,
        stderr=subproc.STREAM,
        preexec_fn=os.setpgrp
    )

    proc_log.info.assert_has_calls([
        call('Starting %s: %r', 'foo', 'foo --help'),
        call('aaa'),
        call('bbb'),
        call('ccc')
    ])

    proc_log.warning.assert_called_once_with('Process %s finished', 'foo')

    proc_log.error.assert_not_called()


@pytest.mark.gen_test
def test_start_tty(subprocess_mock):
    proc_log = Mock()
    with patch('jaffle.process.process.ProcessLogger', return_value=proc_log):
        with patch('jaffle.process.process.os') as os:
            os.environ = {'PATH': '/bin'}
            with patch('jaffle.process.process.Subprocess',
                       return_value=subprocess_mock) as subproc:
                proc = Process(Mock(), 'foo', 'foo --help', env={'BAR': 'bar'}, tty=True)
                yield proc.start()

    subproc.assert_called_once_with(
        ['jaffle', 'tty', 'foo --help'],
        env={'PATH': '/bin', 'BAR': 'bar'},
        stdin=None,
        stdout=subproc.STREAM,
        stderr=subproc.STREAM,
        preexec_fn=os.setpgrp
    )

    proc_log.info.assert_has_calls([
        call('Starting %s: %r', 'foo', 'foo --help'),
        call('aaa'),
        call('bbb'),
        call('ccc')
    ])

    proc_log.warning.assert_called_once_with('Process %s finished', 'foo')

    proc_log.error.assert_not_called()


@pytest.mark.gen_test
def test_start_error(subprocess_mock):
    proc_log = Mock()
    with patch('jaffle.process.process.ProcessLogger', return_value=proc_log):
        with patch('jaffle.process.process.os') as os:
            os.environ = {'PATH': '/bin'}
            with patch('jaffle.process.process.Subprocess', return_value=subprocess_mock):
                def read_until(end):
                    raise IOError('Read error')

                subprocess_mock.stdout.read_until = read_until

                proc = Process(Mock(), 'foo', 'foo --help', env={'BAR': 'bar'})
                yield proc.start()

    proc_log.error.assert_called_once_with('Read error')


@pytest.mark.gen_test
def test_stop(subprocess_mock):
    proc_log = Mock()
    with patch('jaffle.process.process.ProcessLogger', return_value=proc_log):
        with patch('jaffle.process.process.os') as os:
            with patch('jaffle.process.process.Subprocess', return_value=subprocess_mock):
                proc = Process(Mock(), 'foo', 'foo --help', env={'BAR': 'bar'})
                yield proc.start()
                yield proc.stop()

    os.getpgid.assert_called_once_with(subprocess_mock.proc.pid)
    os.killpg.assert_called_once_with(os.getpgid.return_value, signal.SIGTERM)

    subprocess_mock.proc.wait.assert_called_once_with(5)

    subprocess_mock.proc is None


@pytest.mark.gen_test
def test_stop_already_dead(subprocess_mock):
    proc_log = Mock()
    with patch('jaffle.process.process.ProcessLogger', return_value=proc_log):
        with patch('jaffle.process.process.os') as os:
            os.killpg.side_effect = OSError()
            with patch('jaffle.process.process.Subprocess', return_value=subprocess_mock):
                proc = Process(Mock(), 'foo', 'foo --help', env={'BAR': 'bar'})
                yield proc.start()
                yield proc.stop()

    os.getpgid.assert_called_once_with(subprocess_mock.proc.pid)
    os.killpg.assert_called_once_with(os.getpgid.return_value, signal.SIGTERM)

    subprocess_mock.proc.wait.assert_not_called()

    subprocess_mock.proc is None


@pytest.mark.gen_test
def test_stop_force(subprocess_mock):
    proc_log = Mock()
    with patch('jaffle.process.process.ProcessLogger', return_value=proc_log):
        with patch('jaffle.process.process.os') as os:
            with patch('jaffle.process.process.Subprocess', return_value=subprocess_mock):
                subprocess_mock.proc.wait.side_effect = TimeoutExpired(Mock(), 5)

                proc = Process(Mock(), 'foo', 'foo --help', env={'BAR': 'bar'})
                yield proc.start()
                yield proc.stop()

    os.getpgid.assert_has_calls([
        call(subprocess_mock.proc.pid),
        call(subprocess_mock.proc.pid)
    ])

    os.killpg.assert_has_calls([
        call(os.getpgid.return_value, signal.SIGTERM),
        call(os.getpgid.return_value, signal.SIGKILL)
    ])

    subprocess_mock.proc.wait.assert_called_once_with(5)

    subprocess_mock.proc is None
