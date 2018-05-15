# -*- coding: utf-8 -*-

from unittest.mock import patch
from jaffle.status import JaffleStatus, JaffleSession


def test_status_init():
    status = JaffleStatus(1, {'foo': 2}, {'bar': 3})
    assert status.pid == 1
    assert status.raw_namespace == {'foo': 2}
    assert status.runtime_variables == {'bar': 3}
    assert status.sessions == {}
    assert status.apps == {}


def test_status_from_dict():
    with patch('jaffle.status.JaffleSession') as session:
        with patch('jaffle.status.JaffleAppData') as app:
            status = JaffleStatus.from_dict({
                'pid': 1,
                'raw_namespace': {'aaa': 'AAA'},
                'runtime_variables': {'bbb': 'BBB'},
                'sessions': {'foo': {'foo': 2}},
                'apps': {'bar': {'bar': 3}}
            })
    assert status.pid == 1
    assert status.raw_namespace == {'aaa': 'AAA'}
    assert status.runtime_variables == {'bbb': 'BBB'}
    assert status.sessions == {'foo': session.from_dict.return_value}
    assert status.apps == {'bar': app.from_dict.return_value}

    session.from_dict.assert_called_once_with({'foo': 2})
    app.from_dict.assert_called_once_with({'bar': 3})


def test_status_add_session():
    status = JaffleStatus(1, {}, {})

    status.add_session('1', 'foo')
    status.add_session('2', 'bar')

    assert set(status.sessions.keys()) == set(['foo', 'bar'])

    foo = status.sessions['foo']
    assert foo.id == '1'
    assert foo.name == 'foo'
    assert foo.kernel is None

    bar = status.sessions['bar']
    assert bar.id == '2'
    assert bar.name == 'bar'
    assert bar.kernel is None


def test_session():
    with patch('jaffle.status.JaffleKernelData') as kernel:
        session = JaffleSession('1', 'foo', {'my_kernel': {}})

    assert session.id == '1'
    assert session.name == 'foo'
    assert session.kernel is kernel.from_dict.return_value

    kernel.from_dict.assert_called_once_with({'my_kernel': {}})

    with patch('jaffle.status.JaffleKernelData') as kernel:
        session = JaffleSession.from_dict({
            'id': '2',
            'name': 'bar',
            'kernel': {'python3': {}}
        })

    assert session.id == '2'
    assert session.name == 'bar'
    assert session.kernel is kernel.from_dict.return_value

    kernel.from_dict.assert_called_once_with({'python3': {}})

    assert session.to_dict() == {
        'id': '2',
        'name': 'bar',
        'kernel': kernel.from_dict.return_value.to_dict.return_value
    }

    kernel.from_dict.return_value.to_dict.assert_called_once_with()
