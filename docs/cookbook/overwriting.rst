=============================
Overwriting the Configuration
=============================

You might want to add ``jaffle.hcl`` to your source code repository to share it within your team. At the same time, you might want to run Jaffle with your own customized log filtering. Editing the same ``jaffle.hcl`` is hard and it may cause an accidental repository commit. Jaffle provides the following two features to overwrite and customize the base configuration.

1. Merging multiple configurations
2. Setting variable from command-line

`examples/tornado_spa_advanced`_ is the example which demonstrates them.

.. _`examples/tornado_spa_advanced`: https://github.com/yatsu/jaffle/tree/master/examples/tornado_spa_advanced

Merging Multiple Configurations
===============================

You can provide multiple configuration file to ``jaffle start``. For example:

.. code-block:: sh

    $ jaffle start jaffle.hcl my_jaffle.hcl

Jaffle read the first file and then merges the other files one by one. Maps are merged deeply and other elements are overwritten.

Let's say you have this ``jaffle.hcl``.

.. code-block:: hcl
    :linenos:

    variable "watchdog_log_level" {
      default = "info"
    }

    app "watchdog" {
      # ...
      logger {
        level = "${var.watchdog_log_level}"
      }
      # ...
    }

And this ``my_jaffle.hcl``.

.. code-block:: hcl
    :linenos:

    variable "watchdog_log_level" {
      default = "debug" # overwrite "info" => "debug"
    }

The configuration will be merged as follows.

.. code-block:: hcl
    :linenos:

    variable "watchdog_log_level" {
      default = "debug"
    }

    app "watchdog" {
      # ...
      logger {
        level = "${var.watchdog_log_level}"
      }
      # ...
    }

Please refer to the :ref:`merging_multiple_configurations` section of the :doc:`jaffle start Command Reference </commands/start>`.

Setting Variable from Command-line
==================================

You can provide :doc:`variables </config/variable>` from command-line. The example shown in the previous section can be executed with ``debug`` log-level as follows.

.. code-block:: sh

    $ J_VAR_watchdog_log_level=debug jaffle start

You can also set it by ``--variables`` option.

.. code-block:: sh

    $ jaffle start --variables='["watchdog_log_level=debug"]'

Please refer to the :doc:`/config/variable` document.

.. note::

   The source package of Jaffle contains example projects in ``examples`` directory.
   You can see the latest version of them here:
   https://github.com/yatsu/jaffle/tree/master/examples
