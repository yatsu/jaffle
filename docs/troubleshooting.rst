===============
Troubleshooting
===============

Debug Logging
=============

``--debug`` option enables the debug logging of Turret itself.

.. code-block:: sh

    $ turret start --debug

Each app has its own log-level setting. You can set it in ``turret.hcl``.

.. code-block:: hcl

  app "myapp" {
    # ...

    logger {
      level = "debug"
    }
  }

You can also set the log-level using a variable like this.

.. code-block:: hcl

  variable "myapp_log_level" {
    default = "info"
  }

  app "myapp" {
    # ...

    logger {
      level = "${var.myapp_log_level}"
    }
  }

You can switch the log-level by providing the value as an environment variable.

.. code-block:: sh

    $ T_VAR_myapp_log_level=debug turret start

The command-line argument ``--variables`` is also avilable to do the same thing.

.. code-block:: sh

    $ turret start --variables='["myapp_log_level=debug"]'

Turret Console
==============

``turret console`` allows you to open an interactive shell and attaches the session into the running kernel. You can inspect or set variables of running apps in it.

.. code-block:: sh

    $ turret console my_kernel
