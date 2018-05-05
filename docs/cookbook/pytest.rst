========================
Auto-testing with pytest
========================

You can setup auto-testing by using :doc:`/apps/watchdog` and :doc:`/apps/pytest`.

Here is the example ``jaffle.hcl``, which can be used by ``jaffle start``.

.. code-block:: hcl
    :linenos:

    kernel "py_kernel" {}

    app "watchdog" {
      class  = "jaffle.app.watchdog.WatchdogApp"
      kernel = "py_kernel"

      options {
        handlers = [{
          watch_path         = "pytest_example"
          patterns           = ["*.py"]
          ignore_directories = true
          code_blocks        = ["pytest.handle_watchdog_event({event})"]
        }]
      }
    }

    app "pytest" {
      class  = "jaffle.app.pytest.PyTestRunnerApp"
      kernel = "py_kernel"

      options {
        args = ["-s", "-v", "--color=yes"]

        auto_test = [
          "pytest_example/tests/test_*.py",
        ]

        auto_test_map {
          "pytest_example/**/*.py" = "pytest_example/tests/{}/test_{}.py"
        }
      }
    }

- L1: Define the kernel ``py_kernel`` which is used by ``watchdog`` and ``pytest``.
- L3-5: Create WatchdogApp with name ``watchdog`` in the kernel ``py_kernel``.
- L9-11: Let Watchdog_ watch the directory ``pytest_example`` with provided patterns.
- L12: When an event comes, the handler executes this code block. The variable ``pytest`` is an app created later (L17).
- L17-19: Define PyTestRunnerApp with name ``pytest`` in the kernel ``py_kernel``.
- L24-26: When ``pytest_example/tests/test_*.py`` is modified, pytest_ executes it.
- L28-30: When ``pytest_example/**/*.py`` is modified, pytest_ executes the file matched to the pattern ``pytest_example/tests/{}/test_{}.py``.

.. _Watchdog: https://github.com/gorakhargosh/watchdog
.. _pytest: https://pytest.org/

Interactive Shell
=================

You can also use the interactive shell which attaches the session to the running pytest instance:

.. code-block:: sh

    $ jaffle attach pytest

When you hit ``t`` ``TAB`` ``/``, test cases are auto-completed.

Screenshot
==========

.. figure:: pytest_example.gif
   :align: center

.. note::

   The source package of Jaffle contains example projects in ``examples`` directory.
   You can see the latest version of them here:
   https://github.com/yatsu/jaffle/tree/master/examples

   A pytest example is here:
   https://github.com/yatsu/jaffle/tree/master/examples/pytest
