====================
Configuration Syntax
====================

The configuration language of ``jaffle.hcl`` is HCL_ (HashiCorp Configuration Language).

.. _HCL: https://github.com/hashicorp/hcl

The top-level of the configuration can have the following items:

- :doc:`kernel`
- :doc:`app`
- :doc:`process`
- :doc:`job`
- :doc:`logger`
- :doc:`variable`

Example
=======

.. code-block:: hcl

    kernel "py_kernel" {}

    app "watchdog" {
      class  = "jaffle.app.watchdog.WatchdogApp"
      kernel = "py_kernel"

      logger {
        level = "info"
      }

      options {
        handlers = [{
          watch_path         = "my_module"
          patterns           = ["*.py"]
          ignore_directories = true
          functions          = ["pytest.handle_watchdog_event({event})"]
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
          "my_module/tests/test_*.py",
        ]

        auto_test_map {
          "my_module/**/*.py" = "my_module/tests/{}/test_{}.py"
        }
      }
    }

JSON
====

Since JSON is a valid HCL, you can also write the configuration file as JSON. The previous HCL example is same as the following JSON.

.. code-block:: json

    {
      "kernel": {
        "py_kernel": {}
      },
      "app": {
        "watchdog": {
          "class": "jaffle.app.watchdog.WatchdogApp",
          "kernel": "py_kernel",
          "logger": {
            "level": "info"
          },
          "options": {
            "handlers": [
              {
                "watch_path": "my_module",
                "patterns": [
                  "*.py"
                ],
                "ignore_directories": true,
                "functions": [
                  "pytest.handle_watchdog_event({event})"
                ]
              }
            ]
          }
        },
        "pytest": {
          "class": "jaffle.app.pytest.PyTestRunnerApp",
          "kernel": "py_kernel",
          "logger": {
            "level": "info"
          },
          "options": {
            "args": [
              "-s",
              "-v",
              "--color=yes"
            ],
            "auto_test": [
              "my_module/tests/test_*.py"
            ],
            "auto_test_map": {
              "my_module/**/*.py": "my_module/tests/{}/test_{}.py"
            }
          }
        }
      }
    }
