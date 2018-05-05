kernel "py_kernel" {}

app "watchdog" {
  class  = "jaffle.app.watchdog.WatchdogApp"
  kernel = "py_kernel"

  options {
    handlers = [
      {
        watch_path         = "tornado_spa"
        patterns           = ["*.py"]
        ignore_patterns    = ["*/tests/*.py"]
        ignore_directories = true
        clear_cache        = ["tornado_spa"]

        code_blocks = [
          "tornado_app.handle_watchdog_event({event})",
          "pytest.handle_watchdog_event({event})",
        ]
      },
      {
        watch_path         = "tornado_spa/tests"
        patterns           = ["*/test_*.py"]
        ignore_directories = true
        clear_cache        = ["tornado_spa.tests"]

        code_blocks = [
          "pytest.handle_watchdog_event({event})",
        ]
      },
    ]
  }
}

app "tornado_app" {
  class  = "jaffle.app.tornado.TornadoBridgeApp"
  kernel = "py_kernel"
  start  = "tornado_app.start()"

  options {
    app_class   = "tornado_spa.app.ExampleApp"
    args        = ["--port=9999"]
    clear_cache = []
  }
}

app "pytest" {
  class  = "jaffle.app.pytest.PyTestRunnerApp"
  kernel = "py_kernel"

  options {
    args = ["-s", "-v", "--color=yes"]

    auto_test = [
      "tornado_spa/tests/test_*.py",
    ]

    auto_test_map {
      "tornado_spa/**/*.py" = "tornado_spa/tests/{}/test_{}.py"
    }

    clear_cache = []
  }
}

process "frontend" {
  command = "yarn start"
  tty     = true

  env {
    BROWSER = "none"
  }
}

process "jest" {
  command = "yarn test"
  tty     = true
}
