# Turret

Turret is a Python app and process orchestration tool for development
environment leveraging Jupyter kernel and client technology.

"Examples" section below shows what you can do with Turret.

Although Turret is a generic framework, the project is now mainly focusing
on providing auto-test, process management and unified logging for Python
software development.

## Warning

- Turret is in a pre-alpha stage.
    - The API may change without notice during this period.
- Currently Turret can manage only one Jupyter kernel.
- Inter-kernel communication is not implemented yet.

## Examples

### Auto-test

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
      functions          = ["pytest_runner.handle_watchdog_event({event})"]
    }]
  }
}

app "pytest_runner" {
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
kernel `py_kernel`, and assigned to variable `watchdog` and `pytest_runner`
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

- `turret start` starts Turret main process.
- When `turret_pytest_example/example.py` is updated, pytest executes
  `turret_pytest_example/tests/test_example.py`.
- `turret attach pytest_runner` opens an interactive shell and attaches it into
  `pytest_runner` app.
- The pytest interactive shell accepts a test target and executes it in
  a Jupyter kernel of the app.

## Prerequisite

- UNIX-like OS (tested on macOS)
    - Windows is not supported
- Python >= 3.4
- Jupyter Notebook (>= 5.0)
    - Turret does not use Jupyter Notebook but requires its related
      libraries

Turret also requires other libraries written in `requirements.in`. They
are automatically installed by the installer.

## Installation

```sh
$ git clone https://github.com/yatsu/turret
$ cd turret
$ python setup.py install
```

If you use Watchdog and pytest with Turret, install them:

```sh
$ pip install watchdog
$ pip install pytest
```
