# -*- coding: utf-8 -*-

from jaffle.utils import deep_merge


def test_deep_merge():
    a = {}
    b = {}
    result = deep_merge(a, b)
    assert result == {}
    assert result is not a
    assert result is not b

    a = {'a': 1}
    b = {'b': 2, 'a': 2}
    c = {'c': 3, 'a': 3}
    result = deep_merge(a, b, c)
    assert result == {'a': 3, 'b': 2, 'c': 3}
    assert a == {'a': 1}
    assert b == {'b': 2, 'a': 2}
    assert c == {'c': 3, 'a': 3}

    a = {'a': [1, 2]}
    b = {'a': [3, 4]}
    result = deep_merge(a, b)
    assert result == {'a': [3, 4]}
    assert a == {'a': [1, 2]}
    assert b == {'a': [3, 4]}

    a = {'a': {'b': 1, 'd': {'e': 3, 'f': 4}}}
    b = {'a': {'c': 2, 'd': {'e': [1, 2], 'g': 5}}}
    result = deep_merge(a, b)
    assert result == {'a': {'b': 1, 'c': 2, 'd': {'e': [1, 2], 'f': 4, 'g': 5}}}
    assert a == {'a': {'b': 1, 'd': {'e': 3, 'f': 4}}}
    assert b == {'a': {'c': 2, 'd': {'e': [1, 2], 'g': 5}}}


def test_deep_merge_update():
    a = {}
    b = {}
    result = deep_merge(a, b, update=True)
    assert result == {}
    assert result is a
    assert result is not b

    a = {'a': 1}
    b = {'b': 2, 'a': 2}
    c = {'c': 3, 'a': 3}
    result = deep_merge(a, b, c, update=True)
    assert result == {'a': 3, 'b': 2, 'c': 3}
    assert a == {'a': 3, 'b': 2, 'c': 3}
    assert b == {'b': 2, 'a': 2}
    assert c == {'c': 3, 'a': 3}

    a = {'a': [1, 2]}
    b = {'a': [3, 4]}
    result = deep_merge(a, b, update=True)
    assert result == {'a': [3, 4]}
    assert a == {'a': [3, 4]}
    assert b == {'a': [3, 4]}

    a = {'a': {'b': 1, 'd': {'e': 3, 'f': 4}}}
    b = {'a': {'c': 2, 'd': {'e': [1, 2], 'g': 5}}}
    result = deep_merge(a, b, update=True)
    assert result == {'a': {'b': 1, 'c': 2, 'd': {'e': [1, 2], 'f': 4, 'g': 5}}}
    assert a == {'a': {'b': 1, 'c': 2, 'd': {'e': [1, 2], 'f': 4, 'g': 5}}}
    assert b == {'a': {'c': 2, 'd': {'e': [1, 2], 'g': 5}}}
