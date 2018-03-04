# -*- coding: utf-8 -*-

import pytest


class TestCollector(object):
    """
    pytest plugin to collect test items.
    """
    def __init__(self):
        """
        Initializes TestCollector.
        """
        self.test_items = []

    def pytest_collection_modifyitems(self, items):
        """
        pytest callback to be called on modifying collected test items.

        Parameters
        ----------
        items : list[pytest.Item]
            test items detected by pytest.
        """
        for item in items:
            self.test_items.append(item.nodeid)


def collect_test_items():
    """
    Collects test items using TestCollector as a pytest plugin.

    Returns
    -------
    test_items : list[str]
        Test items (e.g. ['example/tests/test_example.py::test_example'])
    """
    test_collector = TestCollector()
    pytest.main(['-qq', '--collect-only'], plugins=[test_collector])
    return test_collector.test_items
