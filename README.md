# Jaffle

[![Build Status](https://travis-ci.org/yatsu/jaffle.svg?branch=master)](https://travis-ci.org/yatsu/jaffle)
[![Documentation Status](https://readthedocs.org/projects/jaffle/badge/?version=latest)](http://jaffle.readthedocs.io/en/latest/?badge=latest)

This project was renamed from 'Turret' to 'Jaffle'.

Jaffle is an automation tool for Python software development, which can do

- Create Python application instances in [Jupyter](http://jupyter.org/)
  kernels
    - The kernel can be attached from the interactive shell (``jaffle
      console`` command)
    - The Python application application can also be attached from its own
      custom interactive shell (``jaffle attach`` command)
- Launch external processes emulating TTY
- Combine log messages of all Python applications and external processes
    - Also supports filtering and reformatting

## Motivation

Recent applications consist of multiple processes. Containers and orchestration
tools for them are great fit for production services, but in a development
environment, process management in a single machine is still important because
developers need to write code and test faster.
[Foreman](https://github.com/ddollar/foreman) and [its
ports](https://github.com/ddollar/foreman#ports) accomplish that.

Jaffle takes this one step further. What if we can launch multiple apps and
developing tools in one Jupyter kernel instance? They can share imported
modules and communicate with each other easily. Also it makes possible to
create a interactive client which connects to a running app using
[jupyter-client](https://github.com/jupyter/jupyter_client) and
[prompt_toolkit](https://github.com/jonathanslenders/python-prompt-toolkit).

## Warning

Jaffle is intended to be a development tool and does not care much about
security. Arbitrary Python code can be executed in ``jaffle.hcl`` and
you should not use it as a part of production environment. ``jaffle.hcl``
is like a Makefile or a shell script included in a source code repository.

## Screenshot

![tornado_spa example](https://github.com/yatsu/jaffle/blob/master/docs/cookbook/tornado_spa_example.gif)

## Documentation

[Jaffle documentation](http://jaffle.readthedocs.io )

## Examples

[examples](https://github.com/yatsu/jaffle/tree/master/examples) directory
includes some example projects and
[Cookbook](http://jaffle.readthedocs.io/en/latest/cookbook/index.html)
section of the document explains about them.

Here is the simplest example.

### Auto-testing with pytest

Source code: [examples/pytest](https://github.com/yatsu/jaffle/tree/master/examples/pytest)

jaffle.hcl

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

The file format of `jaffle.hcl` is [HCL](https://github.com/hashicorp/hcl).

`kernel "py_kernel" {}` creates a Jupyter kernel. "py_kernel" is a kernel
instance name which is referred from apps.

"app" creates an app. In this example, `jaffle.app.watchdog.WatchdogApp` and
`jaffle.app.pytest.PyTestRunnerApp` will be instantiated in the same Jupyter
kernel `py_kernel`, and assigned to variable `watchdog` and `pytest`
respectively.

`WatchdogApp` can have multiple `handlers` which execute `code_blocks` on
detecting filesystem update to a file that matches its `patterns`.

`auto_test` option of `PyTestRunnerApp` includes test file patterns. When
a file is updated which matches to these patterns, the file itself is executed
by pytest.

`auto_test_map` is a map from `.py` file patterns to test file patterns. When
a file matches to the left-hand side, the right-hand side is executed by pytest
replacing `{}`s with matched strings of `**` and `*`.

[Here](http://jaffle.readthedocs.io/en/latest/cookbook/pytest.html) you
can see the screenshot of this example.

Other examples are:

- [Automatic Sphinx Document Build](http://jaffle.readthedocs.io/en/latest/cookbook/sphinx.html)
- [Web Development with Tornado and React](http://jaffle.readthedocs.io/en/latest/cookbook/tornado_spa.html)
- [Jupyter Extension Development](http://jaffle.readthedocs.io/en/latest/cookbook/jupyter_ext.html)

## Prerequisite

- UNIX-like OS
    - Windows is not supported
- Python >= 3.4
- [Jupyter Notebook](https://jupyter.org/) >= 5.0
- [Tornado](http://www.tornadoweb.org/) >= 4.5, < 5

Jupyter Notebook and Tornado will be installed automatically if they do not
exist in your environment. Tornado 5 is not yet supported.

## Installation

Please install as follows until the first release:

```sh
$ git clone https://github.com/yatsu/jaffle
$ cd jaffle
$ python setup.py install
```

You will also probably need pytest:

```sh
$ pip install pytest
```

## License

BSD 3-Clause License

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
- [coloredlogcat.py](http://jsharkey.org/logcat/) and [PID
  Cat](https://github.com/JakeWharton/pidcat)
    - Android logcat modifier. Jaffle's log formatter was inspired by them.
