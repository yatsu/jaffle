# -*- coding: utf-8 -*-

import logging
import pytest
from tornado import gen
from unittest.mock import call, patch, Mock
from jaffle.app.base import app as base_app
from jaffle.app.base.app import BaseJaffleApp


@pytest.fixture(scope='module')
def app_config1():
    return Mock(
        app_name='my_app',
        conf={'logger': {'level': 'debug'}},
        jaffle_port=123,
        jobs_conf={'my_job': {'command': 'my_job --debug'}}
    )


@pytest.fixture(scope='module')
def app_config2():
    return Mock(
        app_name='my_app',
        conf={},
        jaffle_port=123,
        jobs_conf={}
    )


@pytest.mark.gen_test
def test_base_app(subprocess_mock, app_config1):
    conf = {
        'app': {
            'my_app': {
                'logger': {
                    'level': 'debug'
                }
            }
        },
        'job': {
            'my_job': {
                'command': 'my_job --debug'
            }
        }
    }

    base_app.get_ipython = Mock()  # inject get_ipython()

    root_logger = Mock()
    loggers = {}

    def get_logger(name=None):
        if name is None:
            return root_logger
        if name not in loggers:
            loggers[name] = Mock()
        return loggers[name]

    with patch('jaffle.app.base.app.logging.getLogger', get_logger):
        with patch('jaffle.app.base.app.JaffleAppLogHandler') as log_handler:
            with patch('jaffle.app.base.app.Job') as job:
                with patch('jaffle.app.base.app.AppConfig.from_dict', return_value=app_config1):
                    app = BaseJaffleApp(conf)

    assert app.app_name == 'my_app'
    assert app.jaffle_port == 123
    assert app.ipython is base_app.get_ipython.return_value

    app_logger = get_logger('my_app')
    assert app.log is app_logger

    app_logger.setLevel.assert_called_once_with(logging.DEBUG)
    assert app_logger.handlers == [log_handler.return_value]
    assert app_logger.propagate is False

    log_handler.assert_called_once_with('my_app', 123)

    job_logger = get_logger('my_job')
    job_logger.parent is app_logger
    job_logger.setLevel.assert_called_once_with(app_logger.level)
    job.assert_called_once_with(job_logger, 'my_job', 'my_job --debug')

    assert app.jobs == {'my_job': job.return_value}

    app.execute_code('code {} {name}', 1, name='foo')

    app.ipython.run_cell.assert_called_once_with('code 1 foo')

    with patch('jaffle.app.base.app.Subprocess', return_value=subprocess_mock) as subproc:
        yield app.execute_command('foo --bar baz')

    subproc.assert_called_once_with(['foo', '--bar', 'baz'],
                                    stdout=subproc.STREAM, stderr=subproc.STREAM)

    app_logger.info.assert_has_calls([
        call('aaa'),
        call('bbb'),
        call('ccc')
    ])

    modules = {
        'aaa': True,
        'aaa.bbb': True,
        'aaa.bbb.ccc': True,
        'bbb': True,
        'bbb.ccc': True,
        'ccc': True
    }
    with patch('jaffle.app.base.app.sys.modules', modules):
        app.clear_module_cache(['aaa', 'bbb.ccc'])

    assert modules == {
        'bbb': True,
        'ccc': True
    }

    with patch.object(app, 'execute_command') as execute_command:
        future = gen.Future()
        future.set_result(Mock())
        execute_command.return_value = future
        yield app.execute_job('my_job')

    execute_command.assert_called_once_with(job.return_value.command,
                                            logger=job.return_value.log)


@pytest.mark.gen_test
def test_default_log_and_job(subprocess_mock, app_config2):
    conf = {
        'app': {
            'my_app': {}
        }
    }

    base_app.get_ipython = Mock()  # inject get_ipython()

    root_logger = Mock()
    loggers = {}

    def get_logger(name=None):
        if name is None:
            return root_logger
        if name not in loggers:
            loggers[name] = Mock()
        return loggers[name]

    with patch('jaffle.app.base.app.logging.getLogger', get_logger):
        with patch('jaffle.app.base.app.JaffleAppLogHandler') as log_handler:
            with patch('jaffle.app.base.app.AppConfig.from_dict', return_value=app_config2):
                app = BaseJaffleApp(conf)

    assert app.app_name == 'my_app'
    assert app.jaffle_port == 123
    assert app.ipython is base_app.get_ipython.return_value

    app_logger = get_logger('my_app')
    assert app.log is app_logger

    app_logger.setLevel.assert_called_once_with(logging.INFO)
    assert app_logger.handlers == [log_handler.return_value]
    assert app_logger.propagate is False

    log_handler.assert_called_once_with('my_app', 123)

    assert app.jobs == {}

    logger = Mock()
    with patch('jaffle.app.base.app.Subprocess', return_value=subprocess_mock) as subproc:
        yield app.execute_command('foo --bar baz', logger=logger)

    subproc.assert_called_once_with(['foo', '--bar', 'baz'],
                                    stdout=subproc.STREAM, stderr=subproc.STREAM)

    logger.info.assert_has_calls([
        call('aaa'),
        call('bbb'),
        call('ccc')
    ])
