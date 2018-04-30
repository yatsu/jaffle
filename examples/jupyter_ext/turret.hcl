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
        invalidate         = ["jupyter_myext"]
        throttle           = 0.5

        code_blocks = [
          "notebook.handle_watchdog_event({event})",
          "pytest.handle_watchdog_event({event})",
        ]
      },
      {
        patterns           = ["*/tests/test_*.py"]
        ignore_directories = true
        invalidate         = ["jupyter_myext.tests"]
        throttle           = 0.5

        code_blocks = [
          "pytest.handle_watchdog_event({event})",
        ]
      },
      {
        patterns           = ["*.js"]
        ignore_directories = true
        throttle           = 0.5

        code_blocks = [
          "nbext_install.handle_watchdog_event({event})",
        ]
      },
    ]
  }
}

app "notebook" {
  class  = "turret.app.tornado.TornadoBridgeApp"
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

  invalidate = []

  start = "notebook.start()"
}

app "pytest" {
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

  invalidate = []
}

app "nbext_install" {
  class  = "jupyter_myext._devel.NBExtensionInstaller"
  kernel = "py_kernel"

  logger {
    level = "info"
  }
}
