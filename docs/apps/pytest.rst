===============
PyTestRunnerApp
===============

PyTestRunnerApp runs pytest_ on receiving Watchdog events sent from :doc:`WatchdogApp </apps/watchdog>`. That works very fast because PyTestRunnerApp runs pytest_ as a Python function in a Jupyter kernel process instead of executing the external ``py.test`` command, and it also keeps cache of imported modules which do not require reloading.

PyTestRunnerApp also has the :ref:`interactive shell <interactive_shell>` which allows you to run tests interactively.

.. _pytest: https://pytest.org/

Example Configuration
=====================

.. code-block:: hcl

	app "pytest" {
	  class  = "jaffle.app.pytest.PyTestRunnerApp"
	  kernel = "py_kernel"

	  options {
	    args = ["-s", "-v", "--color=yes"]

	    auto_test = [
	      "jaffle_tornado_spa_example/tests/test_*.py",
	    ]

	    auto_test_map {
	      "jaffle_tornado_spa_example/**/*.py" = "jaffle_tornado_spa_example/tests/{}/test_{}.py"
	    }
	  }
	}

Optionns
========

- **args** (list[str] | optional | default: [])

    The pytest arguments.

- **auto_test**

	The file path patterns to be executed by pytest. The pattern syntax is the same as shell glob but supports only ``*`` and ``**``. ``*`` matches arbitrary characters except for ``/`` (slash), whereas ``**`` matches all characters.

- **auto_test_map**

    The file path patterns map to determine test files to be executed. If the event path matches to the left-hand-side pattern, the files which match the right-hand-side will be executed. The pattern syntax is the same as ``auto_test``. The strings matched to ``*`` or ``**`` in the left-hand-side will be expanded into ``{}`` in the right-hand-side one by one.

    .. tip::

       It is recommended to create a Python implimentation file and a unit test file to have one-to-one correspondence to each other. That makes easy to setup ``auto_test_map``.

       If you editor supports jumping to alternative file like vim-projectionist_, it also helps a lot.

       .. _vim-projectionist: https://github.com/tpope/vim-projectionist

- **clear_cache** (list[str] | optional | default: <modules found under the current directory>)

    The module names which will be removed from the module cache (``sys.modules``) before restarting the app. If it is not provided, TornadoBridgeApp searches modules by calling ``setuptools.find_packages()``. Note that the root Python module must be in the current working directory to be found by TornadoBridgeApp. If it is included in a sub-directory, you must specify ``clear_cache`` manually.

.. _interactive_shell:

Interactive Shell
=================

You can use an interactive shell which attaches the session to PyTestRunnerApp running in a Jupyter kernel.

Example:

.. code-block:: sh

	$ jaffle attach pytest

You can type test case names with auto-completion. The tests are executed in the Jupyter kernel.
