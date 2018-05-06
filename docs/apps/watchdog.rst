===========
WatchdogApp
===========

WatchdogApp launches Watchdog handlers with given patterns and callback code blocks. Since Jaffle is initially designed to be an automation tool, WatchdogApp is regarded as the central app among other Jaffle apps.

Watchdog_ is a Python API library and shell utilities to monitor file system events.

.. _Watchdog: https://pythonhosted.org/watchdog/

Example Configuration
=====================

.. code-block:: hcl

    app "watchdog" {
      class  = "jaffle.app.watchdog.WatchdogApp"
      kernel = "py_kernel"

      options {
        handlers = [{
          patterns           = ["*.py"]
          ignore_patterns    = ["*/tests/*.py"]
          ignore_directories = true
          functions          = ["pytest.handle_watchdog_event({event})"]
        }]
      }
    }

Options
=======

- **handlers** (list[dict] | optional | default: [])

   Watchdog handler definitions. The dict format is described below.

Handler dict Format
-------------------

- **watch_path** (str | optional | default: current_directory)

    The directory to be watched by the handler. Both absolute and relative paths are available.

- **patterns** (list[str] | optional | default: [])

    The path matching patterns to execute handler code blocks and jobs. The pattern syntax is the same as Python's fnmatch_. Since the Watchdog event has an absolute file path, you will probably need ``*`` at the beginning of the pattern (e.g.: ``patterns = ["*/foo/*.py"]``).

    .. note::

       The Watchdog pattern syntax and the :doc:`PyTestRunner </apps/pytest>` pattern syntax are difference from each other. They may be changed to be identical in the future release.

.. _fnmatch: https://docs.python.org/3/library/fnmatch.html

- **ignore_patterns** (list[str] | optional | default: [])

    The path matching patterns to be ignored. The pattern syntax is the same as ``patterns``.

- **ignore_directories** (bool | optional | default: false)

    Whether to ignore Watchdog events of directories.

- **throttle** (float | optional | default: 0.0)

    The throttle time in seconds for event handling. When an event is handled, the event handling is disabled until the throttle time passes by. If it is ``0``, the throttling is disabled.

- **debounce** (float | optional | default: 0.0)

    The debounce time in seconds for event handling. The event will be handled only when the debounce time has passed without receiving any other events. If it is ``0``, the debouncing is disabled.

    .. tip::

	   Throttling and debouncing are useful when your editor or any other app does multiple file-system operations at once. For example, when you save a file in an editor, the editor may write the file twice to do auto-formatting. In this case, two events are going to be handled each time you save a file and you might want to handle the event only once. ``throttle`` and ``debounce`` come into play in this situation.

- **code_blocks** (list[str] | optional | default: [])

    The code blocks to be executed by the handler.

- **jobs** (list[str] optional | default: [])

    The jobs to be executed by the handler. Jobs must be defined in :doc:`/config/job` blocks.

- **clear_cache** (list[str] | optional | default: <modules found under the current directory>)

    The module names which will be removed from the module cache (``sys.modules``) before executing handler code blocks.

Integration with Other Apps
===========================

WatchdogApp handler executes Python code written in ``code_blocks``, with replacing the interpolation keyword ``{event}`` with an watchdog.events.FileSystemEvent_ object.

.. _watchdog.events.FileSystemEvent: https://pythonhosted.org/watchdog/api.html#watchdog.events.FileSystemEvent

Example:

.. code-block:: hcl

    code_blocks = ["pytest.handle_watchdog_event({event})"]

:doc:`PyTestRunnerApp </apps/pytest>` and :doc:`TornadoBridgeApp </apps/tornado>` has ``handle_watchdog_event()`` to handle the Watchdog event.
