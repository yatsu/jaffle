# -*- coding: utf-8 -*-

from pathlib import Path
import shlex
import signal
import os
import pytest
import re
from tornado.escape import to_unicode
from tornado.process import Subprocess
from tornado.iostream import StreamClosedError


@pytest.fixture(scope='module')
def jupyter_ext_example_dir():
    cwd_org = Path.cwd()
    os.chdir(Path(__file__).parent.parent.parent.parent.parent / 'examples' / 'jupyter_ext')
    yield Path.cwd()
    os.chdir(cwd_org)


@pytest.mark.gen_test(timeout=10)
def test_jupyter_ext_example(jupyter_ext_example_dir):
    command = 'turret start --disable-color -y'
    proc = Subprocess(shlex.split(command), stdin=None, stderr=Subprocess.STREAM,
                      preexec_fn=os.setpgrp)
    stdout = []
    try:
        while True:
            line_bytes = yield proc.stderr.read_until(b'\n')
            line = to_unicode(line_bytes).rstrip()
            stdout.append(line)
            if re.search(r'Kernel py_kernel \(.*\) is ready', line):
                break
    except StreamClosedError:
        pass

    os.killpg(os.getpgid(proc.proc.pid), signal.SIGINT)

    assert 'Turret port:' in stdout[0]
    assert 'Starting kernel: py_kernel' in stdout[1]
    assert 'Kernel started:' in stdout[2]
    assert 'Initializing turret.app.watchdog.WatchdogApp on py_kernel' in stdout[3]
    assert 'Initializing turret.app.tornado.TornadoApp on py_kernel' in stdout[4]
    assert 'Initializing turret.app.pytest.PyTestRunnerApp on py_kernel' in stdout[5]
    assert 'Initializing jupyter_myext._devel.NBExtensionInstaller on py_kernel' in stdout[6]
