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
        ignore_directories = true
        function           = "pytest_runner.handle_watchdog_event({event})"
      },
      {
        patterns           = ["*/turret_tornado_spa_example/*.py"]
        ignore_patterns    = ["*/tests/*.py"]
        ignore_directories = true
        function           = "tornado_app.handle_watchdog_event({event})"
      },
    ]
  }
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
      "turret_tornado_spa_example/tests/test_*.py",
    ]

    auto_test_map {
      "turret_tornado_spa_example/**/*.py" = "turret_tornado_spa_example/tests/{}/test_{}.py"
    }
  }
}

app "tornado_app" {
  class  = "turret.app.tornado.TornadoApp"
  kernel = "py_kernel"

  logger {
    level = "info"
  }

  options {
    app_cls = "turret_tornado_spa_example.app.ExampleApp"

    argv = [
      "--port=9999",
    ]

    uncache = ["turret_tornado_spa_example"]
  }

  start = "tornado_app.start()"
}
