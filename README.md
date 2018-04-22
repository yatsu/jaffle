# Turret

Turret is a Python app and process orchestration tool for development
environment leveraging [Jupyter](http://jupyter.org/) kernel and client
technology.

"Examples" section below shows what you can do with Turret.

Although Turret is a generic framework, the project is now mainly focusing
on providing auto-test, process management and unified logging for Python
software development.

## Motivation

Recent applications consist of multiple processes. Containers and orchestration
tools for them are great fit for production services, but in a development
environment, process management in a single machine is still important because
developers need to write code and test faster.
[Foreman](https://github.com/ddollar/foreman) and [its
ports](https://github.com/ddollar/foreman#ports) accomplish that.

Turret takes this one step further. What if we can launch multiple apps and
developing tools in one Jupyter kernel instance? They can share imported
modules and communicate with each other easily. Also it makes possible to
create a interactive client which connects to a running app using
[jupyter-client](https://github.com/jupyter/jupyter_client) and
[prompt_toolkit](https://github.com/jonathanslenders/python-prompt-toolkit).

## Warning

- Turret is in a pre-alpha stage.
    - Configurations and API may change without notice during this period.
- Turret does not care much about security.
    - Arbitrary Python code can be used in some part of ``turret.hcl``.
    - You should not use it as a part of production environments.

## Examples

### Simple Python project with auto-test

[examples/pytest](https://github.com/yatsu/turret/tree/master/examples/pytest)
is an example Python project which uses Turret to execute
[pytest](https://docs.pytest.org/) automatically when a `.py` file is updated.

Here is the configuration file of Turret:
[turret.hcl](https://github.com/yatsu/turret/blob/master/examples/pytest/turret.hcl).

```hcl
kernel "py_kernel" {}

app "watchdog" {
  class  = "turret.app.watchdog.WatchdogApp"
  kernel = "py_kernel"

  options {
    handlers = [{
      patterns           = ["*.py"]
      ignore_directories = true
      functions          = ["pytest.handle_watchdog_event({event})"]
    }]
  }
}

app "pytest" {
  class  = "turret.app.pytest.PyTestRunnerApp"
  kernel = "py_kernel"

  options {
    args = ["-s", "-v", "--color=yes"]

    auto_test = [
      "turret_pytest_example/tests/test_*.py",
    ]

    auto_test_map {
      "turret_pytest_example/**/*.py" = "turret_pytest_example/tests/{}/test_{}.py"
    }
  }
}
```

The file format of `turret.hcl` is
[HCL](https://github.com/hashicorp/hc://github.com/hashicorp/hcl). If you
prefer JSON, you can write it as JSON.

`kernel "py_kernel" {}` creates a Jupyter kernel. "py_kernel" is a kernel
instance name which is referred from apps.

"app" creates an app. In this example, `turret.app.watchdog.WatchdogApp` and
`turret.app.pytest.PyTestRunnerApp` will be instantiated in the same Jupyter
kernel `py_kernel`, and assigned to variable `watchdog` and `pytest`
respectively.

`WatchdogApp` can have multiple `handlers` which execute `functions` on
detecting filesystem update to a file that matches its `patterns`.

`auto_test` option of `PyTestRunnerApp` includes test file patterns. When
a file is updated which matches to these patterns, the file itself is executed
by pytest.

`auto_test_map` is a map from `.py` file patterns to test file patterns. When
a file matches to the left-hand side, the right-hand side is executed by pytest
replacing `{}`s with matched strings of `**` and `*`.

The screen capture below shows how they work:

![pytest example](https://github.com/yatsu/turret/blob/master/assets/pytest_example.gif)

- `turret start` starts a Jupyter kernel and instantiates apps in it.
- When `turret_pytest_example/example.py` is updated, pytest executes
  `turret_pytest_example/tests/test_example.py`.
- `turret attach pytest` opens an interactive shell and attaches it into
  `pytest` app.
- The pytest interactive shell accepts a test target and executes it in
  a Jupyter kernel of the app.

### Tornado single-page web app

[examples/tornado_spa](https://github.com/yatsu/turret/tree/master/examples/tornado_spa)
is a single-page app (SPA) project using [Tornado](http://www.tornadoweb.org/).
The front-end is created by [Create React
App](https://github.com/facebook/create-react-app) (CRA).

In the development environment, `yarn start` launches
[webpack-dev-server](https://github.com/webpack/webpack-dev-server) which
serves static contents. The Tornado web app only serves the back-end web API.

This example runs the Tornado web app in a Jupyter kernel and manages
webpack-dev-server as a separated process. You can start them all by just
typing `turret start` and stop them by `Ctrl-C` as if they were one process.
All log messages are unified in the console.

Here is the `turret.hcl`:

```hcl
kernel "py_kernel" {}

app "watchdog" {
  class  = "turret.app.watchdog.WatchdogApp"
  kernel = "py_kernel"

  options {
    handlers = [
      {
        patterns           = ["*.py"]
        ignore_patterns    = ["*/tests/*.py"]
        ignore_directories = true
        uncache            = ["turret_tornado_spa_example"]

        functions = [
          "tornado_app.handle_watchdog_event({event})",
          "pytest.handle_watchdog_event({event})",
        ]
      },
      {
        patterns           = ["*/tests/test_*.py"]
        ignore_directories = true
        uncache            = ["turret_tornado_spa_example.tests"]
        functions          = ["pytest.handle_watchdog_event({event})"]
      },
    ]
  }
}

app "tornado_app" {
  class  = "turret.app.tornado.TornadoApp"
  kernel = "py_kernel"

  options {
    app_cls = "turret_tornado_spa_example.app.ExampleApp"

    argv = [
      "--port=9999",
    ]
  }

  uncache = []

  start = "tornado_app.start()"
}

app "pytest" {
  class  = "turret.app.pytest.PyTestRunnerApp"
  kernel = "py_kernel"

  options {
    args = ["-s", "-v", "--color=yes"]

    auto_test = [
      "turret_tornado_spa_example/tests/test_*.py",
    ]

    auto_test_map {
      "turret_tornado_spa_example/**/*.py" = "turret_tornado_spa_example/tests/{}/test_{}.py"
    }
  }

  uncache = []
}

process "frontend" {
  command = "yarn start"

  env {
    BROWSER = "none"
  }
}
```

![tornado_spa example](https://github.com/yatsu/turret/blob/master/assets/tornado_spa_example.gif)

- `turret start` instantiates apps in the Jupyter kernel and launches
  `frontend` by executing `yarn start`
- When `turret_tornado_spa_example/webapp.py` is updated, pytest executes
  `turret_tornado_spa_example/tests/test_webapp.py` and the Tornado app
  restarts.
- When `src/App.js` is updated, webpack-dev-server recompiles the front-end
  code (This is done outside of Turret).
- `Ctrl-C` terminates the Jupyter kernel and the webpack-dev-server process.

### Jupyter extension development

[examples/jupyter_ext](https://github.com/yatsu/turret/tree/master/examples/jupyter_ext)
is an example project that implements Jupyter serverextension and nbextension.
Turret launches Jupyter Notebook server in a Jupyter kernel and manages server
restart and reinstalling nbextension.

## Prerequisite

- UNIX-like OS (tested on macOS)
    - Windows is not supported
- Python >= 3.4
- Jupyter Notebook >= 5.0

Turret also requires other libraries written in `requirements.in`. They
are automatically installed by the installer.

## Installation

Please install it manually as follows until the first release:

```sh
$ git clone https://github.com/yatsu/turret
$ cd turret
$ pip install -e .
```

If you use Watchdog and pytest with Turret, install them:

```sh
$ pip install watchdog
$ pip install pytest
```

## License

BSD 3-Clause License

## Related Work

- [Watchdog](https://github.com/gorakhargosh/watchdog)
    - Python API and shell utilities to monitor file system events. Turret
      depends on it.
- [pytest-testmon](https://github.com/tarpas/pytest-testmon)
    - pytest plugin to select tests affected by recent changes. It looks code
      coverage to determine which tests should be executed, whereas Turret uses
      simple pattern mapping.
- [pytest-watch](https://github.com/joeyespo/pytest-watch)
    - Continuous pytest runner using Watchdog, which also supports
      notification, before/after hoooks and using a custom runner script. It
      executes pytest as a subprocess.
- [Foreman](https://github.com/ddollar/foreman)
    - Procfile-based process manager.
- [coloredlogcat.py](http://jsharkey.org/logcat/) and [PID
  Cat](https://github.com/JakeWharton/pidcat)
    - Android logcat modifier. Turret's log formatter was inspired by them.
