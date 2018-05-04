===============================
Automatic Sphinx Document Build
===============================

Here is a simple example which generates a Sphinx document on detecting ``*.rst`` update. It assumes ``.rst`` files are stored in ``docs`` directory and the result HTML will be stored in ``docs/_build``.

jaffle.hcl:

.. code-block:: hcl
    :linenos:

    kernel "py_kernel" {
      pass_env = ["PATH"] # required to run sphinx-build in virtualenv
    }

    app "watchdog" {
      class  = "jaffle.app.watchdog.WatchdogApp"
      kernel = "py_kernel"

      options {
        handlers = [{
          patterns           = ["*/docs/*.*"]
          ignore_patterns    = ["*/_build/*"]
          ignore_directories = true
          jobs               = ["sphinx"]
        }]
      }
    }

    job "sphinx" {
      command = "sphinx-build -M html docs docs/_build"
    }

- L1-3: Define the kernel ``py_kernel`` which is used by ``watchdog`` and ``pytest``. You need to pass ``PATH`` environment variable if ``sphinx-build`` is installed in a virtualenv.
- L5-7: Create WatchdogApp with name ``watchdog`` in the kernel ``py_kernel``.
- L10-13: Let Watchdog_ watch the directory ``pytest_example`` with provided patterns.
- L14: When an event comes, the handler executes the job ``sphinx`` which will be defined later (L19-21)
- L19-21: Define ``sphinx`` job to execute ``sphinx-build``

.. note::

   Ignoreing ``_build`` directory is important (L12 of the above example). If you forget that, ``sphinx`` job updates ``_build`` directory and that triggers ``sphinx`` job again. That will be an infinite loop.

Refreshing Browser
==================

Here is another example on macOS which also refreshes Google Chrome's current tab on detecting file updates.

.. code-block:: hcl
    :linenos:
    :emphasize-lines: 16,26-28

    kernel "py_kernel" {
      pass_env = ["PATH"]
    }

    app "watchdog" {
      class  = "jaffle.app.watchdog.WatchdogApp"
      kernel = "py_kernel"

      options {
        handlers = [{
          patterns           = ["*/docs/*.*"]
          ignore_patterns    = ["*/_build/*"]
          ignore_directories = true
          jobs = [
            "sphinx",
            "chrome_refresh",
          ]
        }]
      }
    }

    job "sphinx" {
      command = "sphinx-build -M html docs docs/_build"
    }

    job "chrome_refresh" {
      command = "osascript chrome_refresh.scpt"
    }

You also need the AppleScript file ``chrome_refresh.scpt`` in the current directory as below.

.. code-block:: applescript

    tell application "Google Chrome" to tell the active tab of its first window
        reload
    end tell

.. tip::

   On Linux, maybe you can use xdotool_ to refresh your browser.

   .. _xdotool: http://www.semicomplete.com/projects/xdotool/

.. note::

   The source package of Jaffle contains example projects in ``examples`` directory.
   You can see the latest version of them here:
   https://github.com/yatsu/jaffle/tree/master/examples

   Jaffle uses the above configuration to generate this Sphinx document:
   https://github.com/yatsu/jaffle/tree/master/jaffle.hcl
