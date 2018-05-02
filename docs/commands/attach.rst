=============
jaffle attach
=============

Opens an interactive shell and attaches to the specified app. The app must support attaching. Only :doc:`/apps/pytest` supports this.

Type ``ctrl-c`` or ``ctrl-d`` to stop it.

Usage
=====

.. code-block:: sh

    jaffle attach <app> [options]

Options
=======

- **--debug**

    Set log level to logging.DEBUG (maximize logging output)

- **-y**

    Answer yes to any questions instead of prompting.

- **--disable-color**

    Disable color output.

- **--log-level=<Enum>** (Application.log_level)

    Default: 30

    Choices: (0, 10, 20, 30, 40, 50, 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    Set the log level by value or name.

- **--log-datefmt=<Unicode>** (Application.log_datefmt)

    Default: '%Y-%m-%d %H:%M:%S'

    The date format used by logging formatters for %(asctime)s

- **--log-format=<Unicode>** (Application.log_format)

    Default: '%(time_color)s%(asctime)s.%(msecs).03d%(time_color_end)s %(name_color)s%(name)14s%(name_color_end)s %(level_color)s %(levelname)1.1s %(level_color_end)s %(message)s'

    The Logging format template

- **--runtime-dir=<Unicode>** (BaseJaffleCommand.runtime_dir)
    Default: '.jaffle'

    Runtime directory path.
