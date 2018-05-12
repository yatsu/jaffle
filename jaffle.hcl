variable "watchdog_log_level" {
  default = "info"
}

variable "pytest_log_level" {
  default = "info"
}

kernel "py_kernel" {
  pass_env = ["PATH"] # required to run sphinx-build in virtualenv
}

app "watchdog" {
  class  = "jaffle.app.watchdog.WatchdogApp"
  kernel = "py_kernel"

  logger {
    level = "${var.watchdog_log_level}"
  }

  options {
    handlers = [
      {
        watch_path         = "jaffle"
        patterns           = ["*.py"]
        ignore_patterns    = ["*/examples/*.py"]
        ignore_directories = true
        throttle           = 0.5

        code_blocks = [
          "pytest.handle_watchdog_event({event})",
        ]
      },
      {
        patterns = [
          "*/jaffle/_version.py",
          "*/jaffle/app/*.py",
          "*/docs/*.*",
        ]

        ignore_patterns    = ["*/_build/*", "*/dist/*"]
        ignore_directories = true
        throttle           = 0.5

        jobs = [
          "sphinx",
          "chrome_refresh",
        ]
      },
    ]
  }
}

app "pytest" {
  class  = "jaffle.app.pytest.PyTestRunnerApp"
  kernel = "py_kernel"

  logger {
    level = "${var.pytest_log_level}"

    suppress_regex = [
      "^platform ",
      "^cachedir:",
      "^rootdir:",
      "^plugins:",
    ]
  }

  options {
    args = ["-s", "-v", "--color=yes"]

    auto_test = [
      "jaffle/tests/**/test_*.py",
    ]

    auto_test_map {
      "jaffle/**/*.py" = "jaffle/tests/unit/{}/test_{}.py"
    }
  }
}

job "sphinx" {
  command = "sphinx-build -M html docs docs/_build"
}

job "chrome_refresh" {
  command = "osascript chrome_refresh.scpt"
}
