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
      function           = "pytest_runner.run"
    }]
  }
}

app "pytest_runner" {
  class  = "turret.app.pytest.PyTestRunnerApp"
  kernel = "py_kernel"

  logger {
    level = "debug"
  }
}
