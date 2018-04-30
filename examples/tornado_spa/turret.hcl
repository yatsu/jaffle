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
  class  = "turret.app.watchdog.WatchdogApp"
  kernel = "py_kernel"

  logger {
    level = "${var.watchdog_log_level}"
  }

  options {
    handlers = [
      {
        watch_path         = "turret_tornado_spa_example"
        patterns           = ["*.py"]
        ignore_patterns    = ["*/tests/*.py"]
        ignore_directories = true
        invalidate_modules = ["turret_tornado_spa_example"]
        throttle           = 0.5

        code_blocks = [
          "tornado_app.handle_watchdog_event({event})",
          "pytest.handle_watchdog_event({event})",
        ]
      },
      {
        watch_path         = "turret_tornado_spa_example/tests"
        patterns           = ["*/test_*.py"]
        ignore_directories = true
        invalidate_modules = ["turret_tornado_spa_example.tests"]
        throttle           = 0.5

        code_blocks = [
          "pytest.handle_watchdog_event({event})",
        ]
      },
    ]
  }
}

app "tornado_app" {
  class  = "turret.app.tornado.TornadoBridgeApp"
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
    app_class          = "turret_tornado_spa_example.app.ExampleApp"
    argv               = ["--port=9999"]
    invalidate_modules = []
    threaded           = "${var.tornado_threaded}"
  }
}

app "pytest" {
  class  = "turret.app.pytest.PyTestRunnerApp"
  kernel = "py_kernel"

  logger {
    level = "${var.pytest_log_level}"
  }

  options {
    args = ["-s", "-v", "--color=yes"]

    auto_test = [
      "turret_tornado_spa_example/tests/test_*.py",
    ]

    auto_test_map {
      "turret_tornado_spa_example/**/*.py" = "turret_tornado_spa_example/tests/{}/test_{}.py"
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
