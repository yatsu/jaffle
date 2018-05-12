# -*- coding: utf-8 -*-

import logging
from unittest.mock import Mock
from jaffle.process.logger import ProcessLogger


def test_init():
    logger = logging.getLogger()
    pl = ProcessLogger(logger)

    assert pl.log is logger
    assert pl.suppress_regex == []
    assert pl.replace_regex == []

    pl = ProcessLogger(logger, ['^$', ' +'], [{
        'from': '(.*)',
        'to': 'test: \\1'
    }])
    assert pl.log is logger
    assert pl.suppress_regex == ['^$', ' +']
    assert pl.replace_regex == [{
        'from': '(.*)',
        'to': 'test: \\1'
    }]


def test_emit():
    pl = ProcessLogger(Mock())

    method = Mock()
    pl.emit(method, 'foo')
    method.assert_called_once_with('foo')

    method = Mock()
    pl.emit(method, 'foo %d', 1)
    method.assert_called_once_with('foo %d', 1)

    method = Mock()
    pl.emit(method, 'foo %s', 'FOO', extra={'a': 'AAA'})
    method.assert_called_once_with('foo %s', 'FOO', extra={'a': 'AAA'})


def test_emit_suppress():
    pl = ProcessLogger(Mock(), suppress_regex=['^Hello'])
    method = Mock()
    pl.emit(method, 'Hello, foo')
    method.assert_not_called()
    pl.emit(method, 'Hi, foo')
    method.assert_called_once_with('Hi, foo')


def test_emit_replace():
    pl = ProcessLogger(Mock(), replace_regex=[{
        'from': r'^Hello, (.*)$',
        'to': r'Hi, \1'
    }])
    method = Mock()
    pl.emit(method, 'Hello, foo')
    method.assert_called_once_with('Hi, foo')


def test_debug():
    log = Mock()
    pl = ProcessLogger(log)
    pl.debug('DEBUG %d', 1)
    log.debug.assert_called_once_with('DEBUG %d', 1)


def test_info():
    log = Mock()
    pl = ProcessLogger(log)
    pl.info('INFO %d', 2)
    log.info.assert_called_once_with('INFO %d', 2)


def test_warning():
    log = Mock()
    pl = ProcessLogger(log)
    pl.warning('WARNING %d', 3)
    log.warning.assert_called_once_with('WARNING %d', 3)


def test_error():
    log = Mock()
    pl = ProcessLogger(log)
    pl.error('ERROR %d', 4)
    log.error.assert_called_once_with('ERROR %d', 4)


def test_critical():
    log = Mock()
    pl = ProcessLogger(log)
    pl.critical('CRITICAL %d', 5)
    log.critical.assert_called_once_with('CRITICAL %d', 5)
