kernel "py_kernel" {}

app "watchdog" {
  class  = "turret.app.watchdog.WatchdogApp"
  kernel = "py_kernel"

  logger {
    level = "info"
  }

  options {
    handlers = [
      {
        patterns           = ["*.py"]
        ignore_patterns    = ["*/tests/*.py"]
        ignore_directories = true
        uncache            = ["jupyter_myext"]

        functions = [
          "notebook.handle_watchdog_event({event})",
          "pytest_runner.handle_watchdog_event({event})",
        ]

        throttle = 0.5
      },
      {
        patterns           = ["*/tests/test_*.py"]
        ignore_directories = true
        uncache            = ["jupyter_myext.tests"]

        functions = [
          "pytest_runner.handle_watchdog_event({event})",
        ]

        throttle = 0.5
      },
      {
        patterns           = ["*.js"]
        ignore_directories = true

        functions = [
          "nbext_install.handle_watchdog_event({event})",
        ]

        throttle = 0.5
      },
    ]
  }
}

app "notebook" {
  class  = "turret.app.tornado.TornadoApp"
  kernel = "py_kernel"

  logger {
    level = "info"
  }

  options {
    app_class = "notebook.notebookapp.NotebookApp"

    argv = [
      "--port=9999",
      "--NotebookApp.token=''",
    ]
  }

  uncache = []

  start = "notebook.start()"
}

app "pytest_runner" {
  class  = "turret.app.pytest.PyTestRunnerApp"
  kernel = "py_kernel"

  logger {
    level = "info"
  }

  options {
    args = ["-s", "-v", "--color=yes"]

    auto_test = [
      "jupyter_myext/tests/test_*.py",
    ]

    auto_test_map {
      "jupyter_myext/**/*.py" = "jupyter_myext/tests/{}/test_{}.py"
    }
  }

  uncache = []
}

app "nbext_install" {
  class  = "jupyter_myext._devel.NBExtensionInstaller"
  kernel = "py_kernel"

  logger {
    level = "info"
  }
}
