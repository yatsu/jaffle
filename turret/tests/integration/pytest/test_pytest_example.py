# -*- coding: utf-8 -*-

from pathlib import Path
import shlex
import signal
import os
import pytest
from tornado.escape import to_unicode
from tornado.process import Subprocess
from tornado.iostream import StreamClosedError


@pytest.fixture(scope='module')
def pytest_example_dir():
    cwd_org = Path.cwd()
    os.chdir(Path(__file__).parent.parent.parent.parent.parent / 'examples' / 'pytest')
    yield Path.cwd()
    os.chdir(cwd_org)


@pytest.mark.gen_test(timeout=10)
def test_pytest_example(pytest_example_dir):
    command = 'turret start --disable-color -y'
    proc = Subprocess(shlex.split(command), stdin=None, stderr=Subprocess.STREAM,
                      preexec_fn=os.setpgrp)
    stdout = []
    try:
        while True:
            line = yield proc.stderr.read_until(b'\n')
            stdout.append(to_unicode(line).rstrip())
            if line.endswith(b'Initializing turret.app.pytest.PyTestRunnerApp\n'):
                break
    except StreamClosedError:
        pass

    os.killpg(os.getpgid(proc.proc.pid), signal.SIGINT)

    assert 'Turret port:' in stdout[0]
    assert 'Starting kernel: py_kernel' in stdout[1]
    assert 'Kernel started:' in stdout[2]
    assert 'Initializing turret.app.watchdog.WatchdogApp' in stdout[3]
    assert 'Initializing turret.app.pytest.PyTestRunnerApp' in stdout[4]
