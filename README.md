# Jaffle

[![Build Status](https://travis-ci.org/yatsu/jaffle.svg?branch=master)](https://travis-ci.org/yatsu/jaffle)
[![Documentation Status](https://readthedocs.org/projects/jaffle/badge/?version=latest)](http://jaffle.readthedocs.io/en/latest/?badge=latest)

This project was renamed from 'Turret' to 'Jaffle'.

Jaffle is an automation tool for Python software development, which has the
following features:

- Instantiate Python applications in a [Jupyter](http://jupyter.org/) kernel
  and allows them to interact each other
- Launch external processes
- Combine all log messages and allows filtering and reformatting by regular
  expressions and functions
- Built-in [WatchdogApp](http://jaffle.readthedocs.io/en/latest/apps/watchdog.html)
  watches filesystem events and triggers another app, arbitrary code, and
  functions, which make it possible to setup various automations.

## PyPI Project

[jaffle · PyPI](https://pypi.org/project/jaffle)

## Documentation

[Jaffle documentation](http://jaffle.readthedocs.io)

## Screenshot

![tornado_spa example](https://github.com/yatsu/jaffle/blob/master/docs/cookbook/tornado_example.gif)

## Examples

- [Auto-testing with pytest](http://jaffle.readthedocs.io/en/latest/cookbook/pytest.html)
- [Automatic Sphinx Document Build](http://jaffle.readthedocs.io/en/latest/cookbook/sphinx.html)
- [Web Development with Tornado and React](http://jaffle.readthedocs.io/en/latest/cookbook/tornado_spa.html)
- [Jupyter Extension Development](http://jaffle.readthedocs.io/en/latest/cookbook/jupyter_ext.html)

They are included in [examples](https://github.com/yatsu/jaffle/tree/master/examples) directory.

This is an example of ``jaffle.hcl`` for auto-testing.
You can run it by ``jaffle start``.

```hcl
kernel "py_kernel" {}

app "watchdog" {
  class  = "jaffle.app.watchdog.WatchdogApp"
  kernel = "py_kernel"

  options {
    handlers = [{
      patterns           = ["*.py"]
      ignore_directories = true
      code_blocks        = ["pytest.handle_watchdog_event({event})"]
    }]
  }
}

app "pytest" {
  class  = "jaffle.app.pytest.PyTestRunnerApp"
  kernel = "py_kernel"

  options {
    args = ["-s", "-v", "--color=yes"]

    auto_test = [
      "pytest_example/tests/test_*.py",
    ]

    auto_test_map {
      "pytest_example/**/*.py" = "pytest_example/tests/{}/test_{}.py"
    }
  }
}
```

## Prerequisite

- UNIX-like OS
    - Windows is not supported
- Python >= 3.4
- [Jupyter Notebook](https://jupyter.org/) >= 5.0
- [Tornado](http://www.tornadoweb.org/) >= 4.5, < 5

Jupyter Notebook and Tornado will be installed automatically if they do not
exist in your environment. Tornado 5 is not yet supported.

## Installation

```sh
$ pip install jaffle
```

You will also probably need pytest:

```sh
$ pip install pytest
```

## License

BSD 3-Clause License

## Warning

Jaffle is intended to be a development tool and does not care much about
security. Arbitrary Python code can be executed in ``jaffle.hcl`` and
you should not use it as a part of production environment. ``jaffle.hcl``
is like a Makefile or a shell script included in a source code repository.

## Related Work

- [Watchdog](https://github.com/gorakhargosh/watchdog)
    - Python API and shell utilities to monitor file system events. Jaffle
      depends on it.
- [pytest-testmon](https://github.com/tarpas/pytest-testmon)
    - pytest plugin to select tests affected by recent changes. It looks code
      coverage to determine which tests should be executed, whereas Jaffle uses
      simple pattern mapping.
- [pytest-watch](https://github.com/joeyespo/pytest-watch)
    - Continuous pytest runner using Watchdog, which also supports
      notification, before/after hoooks and using a custom runner script. It
      executes pytest as a subprocess.
- [Foreman](https://github.com/ddollar/foreman)
    - Procfile-based process manager.
- [coloredlogcat.py](http://jsharkey.org/logcat/) and
  [PID Cat](https://github.com/JakeWharton/pidcat)
    - Android logcat modifier. Jaffle's log formatter was inspired by them.
