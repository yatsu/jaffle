============
jaffle start
============

Starts Jaffle.

Type ``ctrl-c`` to stop it.

Usage
=====

.. code-block:: sh

    jaffle start [options] [conf_file, ...]

The default value for ``conf_file`` is ``"jaffle.hcl"``.

If multiple config files are provided, they will be merged into one configuration.

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

- **--variables=<List>** (JaffleStartCommand.variables)

    Default: []

    Value assignments to the :doc:`variables </config/variable>`.

.. _merging_multiple_configurations:

Merging Multiple Configurations
===============================

If you provide multiple configuration files, Jaffle read the first file and then merges the rest one by one. Maps are merged deeply and other elements are overwritten.

Given that we have the following three configurations.

a.hcl:

.. code-block:: hcl

    process "server" {
      command = "start_server"
      env = {
        FOO = 1
      }
    }

b.hcl:

.. code-block:: hcl

    process "server" {
      command = "start_server"
      env = {
        BAR = 2
      }
    }

c.hcl:

.. code-block:: hcl

    process "server" {
      command = "start_server"
      env = {
        FOO = 4
        BAZ = 3
      }
    }

.. code-block:: sh

When we start Jaffle by typing ``jaffle start a.hcl b.hcl c.hcl``, the configuration will be as below:

.. code-block:: hcl

    process "server" {
      command = "start_server"
      env = {
        FOO = 4
        BAR = 2
        BAZ = 3
      }
    }

Resolved variables are passed to the later configurations. Given that we have the following two configurations and use them as ``jaffle start a.hcl b.hcl``.

a.hcl:

.. code-block:: hcl

    variable "server_command" {
      default = "start_server"
    }

    variable "disable_server" {
      default = false
    }

    process "server" {
      command  = "${var.server_command}"
      disabled = "${var.disable_server}"
    }

b.hcl:

.. code-block:: hcl

    variable "disable_server" {
      default = true # switch the default value to true
    }

    process "server" {
      command  = "${var.server_command} --debug"
    }

The configurations will be merged as follows:

.. code-block:: hcl

    variable "server_command" {
      default = "start_server"
    }

    variable "disable_server" {
      default = true
    }

    process "server" {
      command  = "${var.server_command} --debug"
      disabled = "${var.disable_server}"
    }

.. tip::

   The configuration merging is useful when you have a default configuration in your repository and you want to overwrite some part of it.

   Example:

   .. code-block:: sh

       $ jaffle start jaffle.hcl debug.hcl log_filter.hcl
