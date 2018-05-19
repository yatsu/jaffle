# -*- coding: utf-8 -*-

# import pytest
from jaffle.config.value import ConfigValue, ConfigList, ConfigDict


def test_config_value():
    value = ConfigValue()
    assert value.namespace == {}
    assert value.value is None


def test_config_create():
    value = ConfigValue.create([])
    assert isinstance(value, ConfigList)
    assert value.value == []
    assert value.namespace == {}

    value = ConfigValue.create([1, 2, 3], namespace={'name': 'foo'})
    assert isinstance(value, ConfigList)
    assert value.value == [1, 2, 3]
    assert value.namespace == {'name': 'foo'}

    value = ConfigValue.create({})
    assert isinstance(value, ConfigDict)
    assert value.value == {}
    assert value.namespace == {}

    value = ConfigValue.create({'hello': 'world'}, namespace={'name': 'foo'})
    assert isinstance(value, ConfigDict)
    assert value.value == {'hello': 'world'}
    assert value.namespace == {'name': 'foo'}

    value = ConfigValue.create(None)
    assert value is None

    value = ConfigValue.create('hello')
    assert isinstance(value, str)
    assert value == 'hello'


def test_config_list():
    value = ConfigList([])
    assert value.value == []
    assert value.namespace == {}
    assert len(value) == 0

    value = ConfigList([1, 2, {'a': 3}], namespace={'name': 'foo'})
    assert value.value != [1, 2, {'a': 3}]
    assert value.value == [1, 2, ConfigDict({'a': 3}, namespace={'name': 'foo'})]
    assert value.namespace == {'name': 'foo'}
    assert len(value) == 3
    assert value.raw() == [1, 2, {'a': 3}]
    assert value.raw() != [1, 2, ConfigDict({'a': 3}, namespace={'name': 'foo'})]

    assert [v for v in value] == value.value


def test_config_dct():
    value = ConfigDict({})
    assert value.value == {}
    assert value.namespace == {}
    assert len(value) == 0

    value = ConfigDict({'hello': '${name}!', 'no': ['warries', 'problem']},
                       namespace={'name': 'bar'})
    assert value.value != {'hello': '${name}!', 'no': ['warries', 'problem']}
    assert value.value == {'hello': '${name}!',
                           'no': ConfigList(['warries', 'problem'], namespace={'name': 'bar'})}
    assert value.namespace == {'name': 'bar'}
    assert len(value) == 2
    assert value.raw() == {'hello': '${name}!', 'no': ['warries', 'problem']}
    assert value.raw(render=True) == {'hello': 'bar!', 'no': ['warries', 'problem']}

    assert [v for v in value] == list(value.value.keys())
    assert list(value.keys()) == ['hello', 'no']
    assert list(value.values()) == [
        '${name}!',
        ConfigList(['warries', 'problem'], namespace={'name': 'bar'})
    ]
    assert list(value.items()) == [
        ('hello', '${name}!'),
        ('no', ConfigList(['warries', 'problem'], namespace={'name': 'bar'}))
    ]
