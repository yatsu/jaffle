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
        uncache            = ["turret_tornado_spa_example"]

        functions = [
          "tornado_app.handle_watchdog_event({event})",
          "pytest.handle_watchdog_event({event})",
        ]

        throttle = 0.5
      },
      {
        patterns           = ["*/tests/test_*.py"]
        ignore_directories = true
        uncache            = ["turret_tornado_spa_example.tests"]

        functions = [
          "pytest.handle_watchdog_event({event})",
        ]

        throttle = 0.5
      },
    ]
  }
}

app "tornado_app" {
  class   = "turret.app.tornado.TornadoApp"
  kernel  = "py_kernel"
  start   = "tornado_app.start()"
  uncache = []

  logger {
    level = "info"
  }

  options {
    app_class = "turret_tornado_spa_example.app.ExampleApp"

    argv = [
      "--port=9999",
    ]
  }
}

app "pytest" {
  class   = "turret.app.pytest.PyTestRunnerApp"
  kernel  = "py_kernel"
  uncache = []

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
    ignore_regex = ["^\s*$"] # ignore empty message
  }
}

process "jest" {
  command = "yarn test"
  tty     = true

  logger {
    ignore_regex = ["^\s*$"] # ignore empty message
  }
}
