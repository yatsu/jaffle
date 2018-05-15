# -*- coding: utf-8 -*-

import pytest
from unittest.mock import patch, Mock
from jaffle.variables import VariablesNamespace

NOT_FOUND = VariablesNamespace._NOT_FOUND


def test_init():
    vn = VariablesNamespace()
    assert vn._variables == {}
    assert vn._keep_undefined_vars is False

    vn = VariablesNamespace(keep_undefined_vars=True)
    assert vn._keep_undefined_vars is True

    foo_value = Mock(__repr__=lambda x: 'foo_value')
    with patch.object(VariablesNamespace, '_get_hcl_value', return_value=foo_value):
        vn = VariablesNamespace(var_defs={'foo': {}})
    assert vn._variables == {'foo': foo_value}
    assert repr(vn) == "<VariablesNamespace {variables: {'foo': foo_value}}>"


def test_get_hcl_value_undef():
    vn = VariablesNamespace()
    with patch.object(vn, '_get_python_type'):
        value = vn._get_hcl_value('foo', {}, NOT_FOUND)
        assert value == 'null'


def test_get_hcl_value_default():
    vn = VariablesNamespace()
    with patch.object(vn, '_get_python_type', return_value=str):
        value = vn._get_hcl_value('foo', {'default': 'hello'}, NOT_FOUND)
        assert value == 'hello'
        value = vn._get_hcl_value('foo', {'default': None}, NOT_FOUND)
        assert value == 'null'
        value = vn._get_hcl_value('foo', {'default': True}, NOT_FOUND)
        assert value == 'true'
        value = vn._get_hcl_value('foo', {'default': False}, NOT_FOUND)
        assert value == 'false'
        value = vn._get_hcl_value('foo', {'default': 1}, NOT_FOUND)
        assert value == '1'
        value = vn._get_hcl_value('foo', {'default': 1.5}, NOT_FOUND)
        assert value == '1.5'
        value = vn._get_hcl_value('foo', {'default': []}, NOT_FOUND)
        assert value == '[]'
        value = vn._get_hcl_value('foo', {'default': [1, 2, 3]}, NOT_FOUND)
        assert value == '[1, 2, 3]'
        value = vn._get_hcl_value('foo', {'default': {'test': 1}}, NOT_FOUND)
        assert value == '{"test": 1}'
        value = vn._get_hcl_value('foo', {'default': {'test': [1, True, 2.3]}}, NOT_FOUND)
        assert value == '{"test": [1, true, 2.3]}'


def test_get_hcl_value_env_var_str():
    vn = VariablesNamespace()
    with patch.object(vn, '_get_python_type', return_value=str):
        value = vn._get_hcl_value('foo', {'default': None}, 'hello')
        assert value == 'hello'
        value = vn._get_hcl_value('foo', {'default': None}, 'true')
        assert value == 'true'


def test_get_hcl_value_env_var_bool():
    vn = VariablesNamespace()
    with patch.object(vn, '_get_python_type', return_value=bool):
        value = vn._get_hcl_value('foo', {'default': None}, 'true')
        assert value == 'true'
        value = vn._get_hcl_value('foo', {'default': None}, 'false')
        assert value == 'false'
        value = vn._get_hcl_value('foo', {'default': None}, '1')
        assert value == 'true'
        value = vn._get_hcl_value('foo', {'default': None}, '0')
        assert value == 'false'

        with pytest.raises(ValueError) as e:
            vn._get_hcl_value('foo', {'default': None}, '5')
        assert "Cannot convert '5' to bool" in str(e)


def test_get_hcl_value_env_var_int():
    vn = VariablesNamespace()
    with patch.object(vn, '_get_python_type', return_value=int):
        value = vn._get_hcl_value('foo', {'default': None}, '1')
        assert value == '1'

        with pytest.raises(ValueError) as e:
            vn._get_hcl_value('foo', {'default': None}, '1.5')
        assert "Cannot convert '1.5' to int" in str(e)


def test_get_hcl_value_env_var_float():
    vn = VariablesNamespace()
    with patch.object(vn, '_get_python_type', return_value=float):
        value = vn._get_hcl_value('foo', {'default': None}, '1.5')
        assert value == '1.5'
        value = vn._get_hcl_value('foo', {'default': None}, '1')
        assert value == '1.0'

        with pytest.raises(ValueError) as e:
            vn._get_hcl_value('foo', {'default': None}, 'a')
        assert "Cannot convert 'a' to float" in str(e)


def test_get_hcl_value_env_var_list():
    vn = VariablesNamespace()
    with patch.object(vn, '_get_python_type', return_value=list):
        value = vn._get_hcl_value('foo', {'default': None}, '[]')
        assert value == '"[]"'
        value = vn._get_hcl_value('foo', {'default': None}, '[1, true, 2.5, "foo"]')
        assert value == '"[1, true, 2.5, \\\"foo\\\"]"'

        with pytest.raises(ValueError) as e:
            vn._get_hcl_value('foo', {'default': None}, 'a')
        assert "Cannot convert 'a' to list" in str(e)


def test_get_hcl_value_env_var_dict():
    vn = VariablesNamespace()
    with patch.object(vn, '_get_python_type', return_value=dict):
        value = vn._get_hcl_value('foo', {'default': None}, '{}')
        assert value == '"{}"'
        value = vn._get_hcl_value('foo', {'default': None}, '{"foo": 1}')
        assert value == '"{\\\"foo\\\": 1}"'
        value = vn._get_hcl_value('foo', {'default': None}, '{"foo": [true, 2.5]}')
        assert value == '"{\\\"foo\\\": [true, 2.5]}"'

        with pytest.raises(ValueError) as e:
            vn._get_hcl_value('foo', {'default': None}, 'a')
        assert "Cannot convert 'a' to dict" in str(e)


def test_get_python_type_with_type_str():
    vn = VariablesNamespace()

    py_type = vn._get_python_type('foo', 'str', NOT_FOUND)
    assert py_type is str
    py_type = vn._get_python_type('foo', 'bool', NOT_FOUND)
    assert py_type is bool
    py_type = vn._get_python_type('foo', 'int', NOT_FOUND)
    assert py_type is int
    py_type = vn._get_python_type('foo', 'float', NOT_FOUND)
    assert py_type is float
    py_type = vn._get_python_type('foo', 'list', NOT_FOUND)
    assert py_type is list
    py_type = vn._get_python_type('foo', 'dict', NOT_FOUND)
    assert py_type is dict

    with pytest.raises(ValueError) as e:
        vn._get_python_type('foo', 'bar', NOT_FOUND)
    assert "Invalid type for 'foo': 'bar'" in str(e)

    py_type = vn._get_python_type('foo', 'str', True)
    assert py_type is str
    py_type = vn._get_python_type('foo', 'bool', 'xyz')
    assert py_type is bool
    py_type = vn._get_python_type('foo', 'int', 'xyz')
    assert py_type is int
    py_type = vn._get_python_type('foo', 'float', 'xyz')
    assert py_type is float
    py_type = vn._get_python_type('foo', 'list', 'xyz')
    assert py_type is list
    py_type = vn._get_python_type('foo', 'dict', 'xyz')
    assert py_type is dict

    with pytest.raises(ValueError) as e:
        vn._get_python_type('foo', 'bar', 'str')
    assert "Invalid type for 'foo': 'bar'" in str(e)


def test_get_python_type_without_type_str():
    vn = VariablesNamespace()

    py_type = vn._get_python_type('foo', NOT_FOUND, NOT_FOUND)
    assert py_type is str
    py_type = vn._get_python_type('foo', NOT_FOUND, 'FOO')
    assert py_type is str
    py_type = vn._get_python_type('foo', NOT_FOUND, True)
    assert py_type is bool
    py_type = vn._get_python_type('foo', NOT_FOUND, False)
    assert py_type is bool
    py_type = vn._get_python_type('foo', NOT_FOUND, 1)
    assert py_type is int
    py_type = vn._get_python_type('foo', NOT_FOUND, 1.5)
    assert py_type is float
    py_type = vn._get_python_type('foo', NOT_FOUND, [])
    assert py_type is list
    py_type = vn._get_python_type('foo', NOT_FOUND, {})
    assert py_type is dict

    with pytest.raises(ValueError) as e:
        vn._get_python_type('foo', NOT_FOUND, (0,))
    assert "Invalid default value for 'foo': (0,)" in str(e)


def test_getattr():
    vn = VariablesNamespace(keep_undefined_vars=False)
    vn._variables['foo'] = 1

    foo = vn.foo
    assert foo == 1

    with pytest.raises(KeyError) as e:
        vn.bar
    assert 'bar' in str(e)

    vn = VariablesNamespace(keep_undefined_vars=True)
    vn._variables['bar'] = 2

    bar = vn.bar
    assert bar == 2

    foo = vn.foo
    assert foo == '${var.foo}'


def test_call():
    vn = VariablesNamespace()
    vn._variables['foo'] = 1

    foo = vn('foo')
    assert foo == 1
    foo = vn('foo', 2)
    assert foo == 1

    bar = vn('bar')
    assert bar is None
    bar = vn('bar', True)
    assert bar is True
