# Turret

Turret is a Python app and process orchestration tool for development
environment leveraging Jupyter kernel and client technology.

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

`kernel "py_kernel" {}` creates a Jupyter kernel. "py_kernel" is a kernel
instance name which is referred from apps.

"app" creates an app. In this example, `watchdog` and `pytest_runner` will
be launched in the same Jupyter kernel `py_kernel`. They are assigned
a variable name `watchdog` and `pytest_runner` 

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
