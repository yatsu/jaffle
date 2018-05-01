variable "watchdog_log_level" {
  default = "info"
}

variable "tornado_log_level" {
  default = "info"
}

variable "pytest_log_level" {
  default = "info"
}

variable "tornado_threaded" {
  default = false
}

variable "disable_frontend" {
  default = false
}

variable "disable_jest" {
  default = false
}

kernel "py_kernel" {}

app "watchdog" {
  class  = "jaffle.app.watchdog.WatchdogApp"
  kernel = "py_kernel"

  logger {
    level = "${var.watchdog_log_level}"
  }

  options {
    handlers = [
      {
        watch_path         = "tornado_spa"
        patterns           = ["*.py"]
        ignore_patterns    = ["*/tests/*.py"]
        ignore_directories = true
        invalidate_modules = ["tornado_spa"]
        throttle           = 0.5

        code_blocks = [
          "tornado_app.handle_watchdog_event({event})",
          "pytest.handle_watchdog_event({event})",
        ]
      },
      {
        watch_path         = "tornado_spa/tests"
        patterns           = ["*/test_*.py"]
        ignore_directories = true
        invalidate_modules = ["tornado_spa.tests"]
        throttle           = 0.5

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

  logger {
    level = "${var.tornado_log_level}"

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
    app_class          = "tornado_spa.app.ExampleApp"
    args               = ["--port=9999"]
    invalidate_modules = []
    threaded           = "${var.tornado_threaded}"
  }
}

app "pytest" {
  class  = "jaffle.app.pytest.PyTestRunnerApp"
  kernel = "py_kernel"

  logger {
    level = "${var.pytest_log_level}"
  }

  options {
    args = ["-s", "-v", "--color=yes"]

    auto_test = [
      "tornado_spa/tests/test_*.py",
    ]

    auto_test_map {
      "tornado_spa/**/*.py" = "tornado_spa/tests/{}/test_{}.py"
    }

    invalidate_modules = []
  }
}

process "frontend" {
  command  = "yarn start"
  tty      = true
  disabled = "${var.disable_frontend}"

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
  command  = "yarn test"
  tty      = true
  disabled = "${var.disable_jest}"

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
