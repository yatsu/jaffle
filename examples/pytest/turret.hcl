kernel "py_kernel" {}

app "watchdog" {
  class  = "turret.app.watchdog.WatchdogApp"
  kernel = "py_kernel"

  logger {
    level = "debug"
  }

  options {
    handlers = [{
      patterns           = ["*.py"]
      ignore_directories = true
      function           = "pytest_runner.handle_watchdog_event({event})"
    }]
  }
}

app "pytest_runner" {
  class  = "turret.app.pytest.PyTestRunnerApp"
  kernel = "py_kernel"

  logger {
    level = "debug"
  }

  options {
    args = ["-s", "-v"]

    auto_test = [
      "turret_pytest_example/tests/test_*.py",
    ]

    auto_test_map {
      "turret_pytest_example/*.py" = "turret_pytest_example/tests/test_{}.py"
    }
  }
}
