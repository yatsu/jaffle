kernel "py_kernel" {}

app "watchdog" {
  class  = "jaffle.app.watchdog.WatchdogApp"
  kernel = "py_kernel"

  options {
    handlers = [
      {
        patterns           = ["*.py"]
        ignore_patterns    = ["*/tests/*.py"]
        ignore_directories = true
        invalidate_modules = ["jupyter_myext"]

        code_blocks = [
          "notebook.handle_watchdog_event({event})",
          "pytest.handle_watchdog_event({event})",
        ]
      },
      {
        patterns           = ["*/tests/test_*.py"]
        ignore_directories = true
        invalidate_modules = ["jupyter_myext.tests"]

        code_blocks = [
          "pytest.handle_watchdog_event({event})",
        ]
      },
      {
        patterns           = ["*.js"]
        ignore_directories = true

        code_blocks = [
          "nbext_install.handle_watchdog_event({event})",
        ]
      },
    ]
  }
}

app "notebook" {
  class  = "jaffle.app.tornado.TornadoBridgeApp"
  kernel = "py_kernel"

  options {
    app_class = "notebook.notebookapp.NotebookApp"

    args = [
      "--port=9999",
      "--NotebookApp.token=''",
    ]

    invalidate_modules = []
  }

  start = "notebook.start()"
}

app "pytest" {
  class  = "jaffle.app.pytest.PyTestRunnerApp"
  kernel = "py_kernel"

  options {
    args = ["-s", "--color=yes"]

    auto_test = [
      "jupyter_myext/tests/test_*.py",
    ]

    auto_test_map {
      "jupyter_myext/**/*.py" = "jupyter_myext/tests/{}/test_{}.py"
    }

    invalidate_modules = []
  }
}

app "nbext_install" {
  class  = "jupyter_myext._devel.NBExtensionInstaller"
  kernel = "py_kernel"
}
