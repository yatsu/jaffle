======================================
Web Development with Tornado and React
======================================

Here is an example Jaffle setup for the web development which uses Tornado and React to build the back-end API and the front-end web interface respectively.

It does:

- Launch the Tornado application including HTTP server
- Launch the Webpack dev server as an external process by executing ``yarn start``
- Launch Jest as an external process by executing ``yarn test``
- Restart the Tornado application when a related file is updated
- Execute pytest_ when a related file is updated

.. _pytest: https://pytest.org/

jaffle.hcl:

.. code-block:: hcl
    :linenos:

    kernel "py_kernel" {}

    app "watchdog" {
      class  = "jaffle.app.watchdog.WatchdogApp"
      kernel = "py_kernel"

      options {
        handlers = [
          {
            watch_path         = "tornado_spa"
            patterns           = ["*.py"]
            ignore_patterns    = ["*/tests/*.py"]
            ignore_directories = true
            invalidate_modules = ["tornado_spa"]

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

      options {
        app_class          = "tornado_spa.app.ExampleApp"
        args               = ["--port=9999"]
        invalidate_modules = []
      }
    }

    app "pytest" {
      class  = "jaffle.app.pytest.PyTestRunnerApp"
      kernel = "py_kernel"

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
      command = "yarn start"
      tty     = true

      env {
        BROWSER = "none"
      }
    }

    process "jest" {
      command = "yarn test"
      tty     = true
    }

Screenshot
==========

.. figure:: tornado_example.gif

.. note::

   The source package of Jaffle contains example projects in ``examples`` directory.
   You can see the latest version of them here:
   https://github.com/yatsu/jaffle/tree/master/examples

   A Tornado and React example is here:
   https://github.com/yatsu/jaffle/tree/master/examples/tornado_spa
