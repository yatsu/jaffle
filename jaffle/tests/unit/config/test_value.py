# -*- coding: utf-8 -*-

import pytest
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

    assert value[0] == 1
    assert value[1] == 2
    assert value[2] == ConfigDict({'a': 3}, namespace={'name': 'foo'})
    with pytest.raises(IndexError) as e:
        value[3]
    assert 'out of range' in str(e)

    assert value.get(0) == 1
    assert value.get(1) == 2
    assert value.get(2) == ConfigDict({'a': 3}, namespace={'name': 'foo'})
    assert value.get(3) is None
    assert value.get(3, 3) == 3

    assert value.get(0, raw=True) == 1
    assert value.get(1, raw=True) == 2
    assert value.get(2, raw=True) == {'a': 3}
    assert value.get(3, 3, raw=True) == 3

    assert value.get_raw(0) == 1
    assert value.get_raw(1) == 2
    assert value.get_raw(2) == {'a': 3}
    with pytest.raises(IndexError) as e:
        value.get_raw(3)
    assert 'out of range' in str(e)
    assert value.get_raw(3, 3) == 3


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

    assert set([v for v in value]) == set(value.value.keys())
    assert set(value.keys()) == set(['hello', 'no'])
    values = list(value.values())
    assert len(values) == 2
    assert '${name}!' in values
    assert ConfigList(['warries', 'problem'], namespace={'name': 'bar'}) in values
    items = list(value.items())
    assert len(items) == 2
    assert ('hello', '${name}!') in items
    assert ('no', ConfigList(['warries', 'problem'], namespace={'name': 'bar'})) in items

    assert value['hello'] == '${name}!'
    assert value['no'] == ConfigList(['warries', 'problem'], namespace={'name': 'bar'})
    with pytest.raises(KeyError) as e:
        value['foo']
    assert 'foo' in str(e)

    assert value.get('hello') == '${name}!'
    assert value.get('no') == ConfigList(['warries', 'problem'], namespace={'name': 'bar'})
    assert value.get('foo') is None
    assert value.get('hello', render=True) == 'bar!'

    assert value.get('hello', raw=True) == '${name}!'
    assert value.get('no', raw=True) == ['warries', 'problem']
    assert value.get('foo', raw=True) is None
    assert value.get('foo', 1, raw=True) == 1
    assert value.get('hello', raw=True, render=True) == 'bar!'

    assert value.get_raw('hello') == 'bar!'
    assert value.get_raw('no') == ['warries', 'problem']
    with pytest.raises(KeyError) as e:
        value.get_raw('foo')
    assert 'foo' in str(e)
    assert value.get_raw('foo', 1) == 1
    assert value.get_raw('hello', render=False) == '${name}!'

    assert value.hello == '${name}!'
    assert value.no == ConfigList(['warries', 'problem'], namespace={'name': 'bar'})
    with pytest.raises(AttributeError) as e:
        value.foo
    assert "'ConfigDict' object has no attribute 'foo'" in str(e)
