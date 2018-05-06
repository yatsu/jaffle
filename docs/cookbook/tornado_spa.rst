======================================
Web Development with Tornado and React
======================================

This is an example Jaffle configuration for the web development which uses Tornado_ and React_ to build the back-end API and the front-end web interface respectively.

It does:

- Launch the Tornado application including HTTP server
- Launch the Webpack dev server as an external process by executing ``yarn start``
- Launch Jest as an external process by executing ``yarn test``
- Restart the Tornado application when a related file is updated
- Execute pytest_ when a related file is updated

This page assumes that you have already know the basic configuration for a pytest_. If not, please read the section :doc:`pytest`.

.. _Tornado: http://www.tornadoweb.org/
.. _React: https://reactjs.org/
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
            clear_cache        = ["tornado_spa"]

            code_blocks = [
              "tornado_app.handle_watchdog_event({event})",
              "pytest.handle_watchdog_event({event})",
            ]
          },
          {
            watch_path         = "tornado_spa/tests"
            patterns           = ["*/test_*.py"]
            ignore_directories = true
            clear_cache        = ["tornado_spa.tests"]

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
        app_class   = "tornado_spa.app.ExampleApp"
        args        = ["--port=9999"]
        clear_cache = []
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

        clear_cache = []
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

Clearing Module Cache
=====================

Since two applications ``tornado_app`` and ``pytest`` run in the same Jupyter kernel and share the same Python modules in memory, you should manually configure the cache clear. By default :doc:`/apps/tornado` and :doc:`/apps/pytest` clear the modules found under the current directory on receiving an Watchdog event. That causes duplicated cache clear on the same module. To prevent that, the configuration above has ``clear_cache = []`` in both ``tornado_app`` and ``pytest`` to disable cache clear and has ``clear_cache = ["tornado_spa"]`` in ``watchdog`` to let :doc:`/apps/watchdog` clear the module cache instead.

.. note::

    If ``clear_cache`` configuration is incorrect, :doc:`/apps/tornado` or :doc:`/apps/pytest` may not reload Python modules.


Screenshot
==========

.. figure:: tornado_example.gif
   :align: center

.. note::

   The source package of Jaffle contains example projects in ``examples`` directory.
   You can see the latest version of them here:
   https://github.com/yatsu/jaffle/tree/master/examples

   A Tornado and React example is here:
   https://github.com/yatsu/jaffle/tree/master/examples/tornado_spa
