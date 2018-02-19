# -*- coding: utf-8 -*-

from turret_pytest_example.example import hello


def test_example():
    assert hello() == 'Hello, World!'
