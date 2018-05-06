=============================
Jupyter Extension Development
=============================

This page assumes that you have already know the basic configuration for a Tornado application. If not, please read the section :doc:`tornado_spa`.

To execute `examples/jupyter_ext`_, you need to setup the Python project and install Jupyter serverextension and nbextension first.

Example setup:

.. code-block:: sh

    $ cd example/jupyter_ext
    $ pip install -e .
    $ jupyter serverextension install jupyter_myext --user
    $ jupyter nbextension install jupyter_myext --user

.. _`examples/jupyter_ext`: https://github.com/yatsu/jaffle/tree/master/examples/jupyter_ext

Here is the Jaffle configuration.

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
            patterns           = ["*.py"]
            ignore_patterns    = ["*/tests/*.py"]
            ignore_directories = true
            clear_cache        = ["jupyter_myext"]

            code_blocks = [
              "notebook.handle_watchdog_event({event})",
              "pytest.handle_watchdog_event({event})",
            ]
          },
          {
            patterns           = ["*/tests/test_*.py"]
            ignore_directories = true
            clear_cache        = ["jupyter_myext.tests"]

            code_blocks = [
              "pytest.handle_watchdog_event({event})",
            ]
          },
          {
            patterns           = ["*.js"]
            ignore_directories = true

            code_blocks = [
              "nbext_install.handle_watchdog_event({event})",
            ]
          },
        ]
      }
    }

    app "notebook" {
      class  = "jaffle.app.tornado.TornadoBridgeApp"
      kernel = "py_kernel"

      options {
        app_class = "notebook.notebookapp.NotebookApp"

        args = [
          "--port=9999",
          "--NotebookApp.token=''",
        ]

        clear_cache = []
      }

      start = "notebook.start()"
    }

    app "pytest" {
      class  = "jaffle.app.pytest.PyTestRunnerApp"
      kernel = "py_kernel"

      options {
        args = ["-s", "--color=yes"]

        auto_test = [
          "jupyter_myext/tests/test_*.py",
        ]

        auto_test_map {
          "jupyter_myext/**/*.py" = "jupyter_myext/tests/{}/test_{}.py"
        }

        clear_cache = []
      }
    }

    app "nbext_install" {
      class  = "jupyter_myext._devel.NBExtensionInstaller"
      kernel = "py_kernel"
    }

- L10-28: The handler configuration of pytest_ execution and Tornado restart, same as the example: :doc:`tornado_spa`.
- L29-36: The handler configuration to install nbextension on detecting ``.js`` file update.
- L41-57: Launch Jupyter notebook server via ``TornadoBridgeApp`` with the main IO loop of the kernel process.
- L78-81: The definition of an app that installs the nbextension.

.. _pytest: https://pytest.org/

.. tip::

    This example uses ``NBExtensionInstaller`` to install the Jupyter nbextension. You can define a :doc:`/config/job` that executes ``jupyter nbextension install --overwrite`` instead. If you do so, be sure to set ``pass_env = ["PATH"]`` in the :doc:`/config/kernel` section if Jupyter is installed in a virtualenv.

.. note::

   The source package of Jaffle contains example projects in ``examples`` directory.
   You can see the latest version of them here:
   https://github.com/yatsu/jaffle/tree/master/examples

   A Jupyter extension example is here:
   https://github.com/yatsu/jaffle/tree/master/examples/jupyter_ext
