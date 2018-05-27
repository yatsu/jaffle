# -*- coding: utf-8 -*-

import pytest
from tornado import gen
from tornado.iostream import StreamClosedError
from tornado.platform.asyncio import AsyncIOMainLoop
from unittest.mock import Mock


@pytest.fixture
def io_loop():
    return AsyncIOMainLoop()


@pytest.fixture(scope='function')
def subprocess_mock():
    stdout = '''
aaa
bbb
ccc
'''.strip().split('\n')

    lineno = 0

    @gen.coroutine
    def read_until(end):
        nonlocal lineno
        yield gen.sleep(0.01)
        if lineno == len(stdout):
            raise StreamClosedError()
        lineno += 1
        return '{}\n'.format(stdout[lineno - 1])

    return Mock(stdout=Mock(read_until=read_until))
