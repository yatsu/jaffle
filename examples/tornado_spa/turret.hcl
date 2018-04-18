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
        invalidate         = ["turret_tornado_spa_example"]
        throttle           = 0.5

        functions = [
          "tornado_app.handle_watchdog_event({event})",
          "pytest.handle_watchdog_event({event})",
        ]
      },
      {
        patterns           = ["*/tests/test_*.py"]
        ignore_directories = true
        invalidate         = ["turret_tornado_spa_example.tests"]
        throttle           = 0.5

        functions = [
          "pytest.handle_watchdog_event({event})",
        ]
      },
    ]
  }
}

app "tornado_app" {
  class      = "turret.app.tornado.TornadoApp"
  kernel     = "py_kernel"
  start      = "tornado_app.start()"
  invalidate = []

  logger {
    level = "info"

    replace_regex = [
      {
        from = "^([12]\\d{2}) "
        to   = "\033[32m\\1\033[0m "
      },
      {
        from = "^(3\\d{2}) "
        to   = "\033[33m\\1\033[0m "
      },
      {
        from = "^([45]\\d{2}) "
        to   = "\033[31m\\1\033[0m "
      },
    ]
  }

  options {
    app_class = "turret_tornado_spa_example.app.ExampleApp"

    argv = [
      "--port=9999",
    ]
  }
}

app "pytest" {
  class      = "turret.app.pytest.PyTestRunnerApp"
  kernel     = "py_kernel"
  invalidate = []

  logger {
    level = "info"
  }

  options {
    args = ["-s", "-v", "--color=yes"]

    auto_test = [
      "turret_tornado_spa_example/tests/test_*.py",
    ]

    auto_test_map {
      "turret_tornado_spa_example/**/*.py" = "turret_tornado_spa_example/tests/{}/test_{}.py"
    }
  }
}

process "frontend" {
  command = "yarn start"
  tty     = true

  env {
    BROWSER = "none"
  }

  logger {
    suppress_regex = [
      "^\\s*$",   # ignore empty message
      "yarn run",
    ]
  }
}

process "jest" {
  command = "yarn test"
  tty     = true

  logger {
    suppress_regex = [
      "^\\s*$",   # ignore empty message
      "yarn run",
    ]

    replace_regex = [
      {
        from = " Press (\\S+) "
        to   = " Press `\\1` "
      },
    ]
  }
}
