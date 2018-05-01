kernel "py_kernel" {
  pass_env = ["PATH"] # required to run sphinx-build in virtualenv
}

app "watchdog" {
  class  = "jaffle.app.watchdog.WatchdogApp"
  kernel = "py_kernel"

  logger {
    level = "info"
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

        ignore_patterns    = ["*/_build/*"]
        ignore_directories = true
        throttle           = 0.5

        jobs = [
          "sphinx",
        ]
      },
    ]
  }
}

app "pytest" {
  class  = "jaffle.app.pytest.PyTestRunnerApp"
  kernel = "py_kernel"

  logger {
    level          = "info"
    suppress_regex = ["^platform "]
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
