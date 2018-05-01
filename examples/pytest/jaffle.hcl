kernel "py_kernel" {}

app "watchdog" {
  class  = "jaffle.app.watchdog.WatchdogApp"
  kernel = "py_kernel"

  logger {
    level = "info"
  }

  options {
    handlers = [{
      watch_path         = "pytest_example"
      patterns           = ["*.py"]
      ignore_directories = true
      code_blocks        = ["pytest.handle_watchdog_event({event})"]
    }]
  }
}

app "pytest" {
  class  = "jaffle.app.pytest.PyTestRunnerApp"
  kernel = "py_kernel"

  logger {
    level = "info"
  }

  options {
    args = ["-s", "-v", "--color=yes"]

    auto_test = [
      "pytest_example/tests/test_*.py",
    ]

    auto_test_map {
      "pytest_example/**/*.py" = "pytest_example/tests/{}/test_{}.py"
    }
  }
}
