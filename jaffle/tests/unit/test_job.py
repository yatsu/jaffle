# -*- coding: utf-8 -*-

from unittest.mock import Mock
from jaffle.job import Job


def test_job():
    log = Mock()
    job = Job(log, 'foo', 'foo --help')

    assert job.log is log
    assert job.name == 'foo'
    assert job.command == 'foo --help'
