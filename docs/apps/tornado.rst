================
TornadoBridgeApp
================

TornadoBridgeApp manages a Tornado application in IPython kernels running in a Jaffle.

Example Configuration
=====================

.. code-block:: hcl

    app "tornado_app" {
      class  = "jaffle.app.tornado.TornadoBridgeApp"
      kernel = "py_kernel"
      start  = "tornado_app.start()"

      logger {
        level = "info",
      }

      options {
        app_class          = "my_module.app.ExampleApp"
        argv               = ["--port=9999"]
        threaded           = true
        clear_cache = ["my_module"]
      }
    }

Options
=======

- **app_class** (str | required | default: undefined)

    The Tornado application class to be launched in a kernel. It must be a fully qualified class name which begins from the top module name joined with ``.``, e.g. ``foo.bar.BazApp``.

- **argv** (list[str] | optional | default: [])

    The arguments to the Tornado application. They will be passed directly to ``__init__()`` of the class.

- **threaded** (bool | optional | default: false)

    Whether to launch the app in an independent IO loop thread. Tornado applications can basically be launched in the main thread and share the IO loop with other apps and the Jaffle itself. However, some apps cannot dispose all running functions from the IO loop and that makes troubles on calling ``start()`` and ``stop()`` several times, because the remaining functions may cause errors. When ``threaded`` is true, the app uses its own IO loop which will be stopped together with the app itself.

- **clear_cache** (list[str] | optional | default: <modules found under the current directory>)

    The module names which will be removed from the module cache (``sys.modules``) before restarting the app. If it is not provided, TornadoBridgeApp searches modules by calling ``setuptools.find_packages()``. Note that the root Python module must be in the current working directory to be found by TornadoBridgeApp. If it is included in a sub-directory, you must specify ``clear_cache`` manually.

Available Tornado Applications
==============================

TornadoBridgeApp assumes that the Tornado application has ``start()`` and ``stop()`` and they meet the following requirements:

- ``start()`` gets the IOLoop by calling ``tornado.ioloop.IOLoop.current()``.
- ``IOLoop.start()`` is called only from ``start()``.
- ``IOLoop.stop()`` is called only from an IOLoop callback which is added by ``stop()``.

Example:

.. code-block:: python

    class ExampleApp(Application):

        def start(self):
            self.io_loop = ioloop.IOLoop.current()
            try:
                self.io_loop.start()
            except KeyboardInterrupt:
                self.log.info('Interrupt')

        def stop(self):
            def _stop():
                self.http_server.stop()
                self.io_loop.stop()
            self.io_loop.add_callback(_stop)

They are required because Jaffle must protect the main IOLoop not to be terminated or overwritten by the app. If your application cannot meet the requirements, you can create a custom Jaffle app inheriting ``TornadoBridgeApp``.

Integration with :doc:`watchdog`
================================

``TornadoBridgeApp.handle_watchdog_event()`` handles an Watchdog event sent from WatchdogApp. It restarts the Tornado application.

Example WatchdogApp configuration:

.. code-block:: hcl

    app "watchdog" {
      class  = "jaffle.app.watchdog.WatchdogApp"
      kernel = "py_kernel"

      options {
        handlers = [
          {
            patterns           = ["*.py"]
            ignore_directories = true
            functions          = ["my_app.handle_watchdog_event({event})"]
          },
        ]
      }
    }

    app "my_app" {
      class  = "jaffle.app.tornado.TornadoBridgeApp"
      kernel = "py_kernel"
      start  = "tornado_app.start()"

      options {
        app_class = "my_module.app.ExampleApp"
      }
    }
