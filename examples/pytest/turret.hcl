kernel "py_kernel" {}

app "watchdog" {
  class  = "turret.app.watchdog.WatchdogApp"
  kernel = "py_kernel"

  logger {
    level = "info"
  }

  options {
    handlers = [{
      watch_path         = "turret_pytest_example"
      patterns           = ["*.py"]
      ignore_directories = true
      code_blocks        = ["pytest.handle_watchdog_event({event})"]
    }]
  }
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
      "turret_pytest_example/tests/test_*.py",
    ]

    auto_test_map {
      "turret_pytest_example/**/*.py" = "turret_pytest_example/tests/{}/test_{}.py"
    }
  }
}
