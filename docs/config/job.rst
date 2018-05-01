===
job
===

The ``job`` block configures a job which can be executed from a Jaffle app.

Example
=======

.. code-block:: hcl

    job "sphinx" {
      command = "sphinx-build -M html docs docs/_build"
    }

Here is an :doc:`/apps/watchdog` configuration which executes the job:

.. code-block:: hcl

    app "watchdog" {
      class  = "jaffle.app.watchdog.WatchdogApp"
      kernel = "py_kernel"

      options {
        handlers = [
          {
            patterns           = ["*/my_module/*.py", "*/docs/*.*"]
            ignore_patterns    = ["*/_build/*"]
            ignore_directories = true
            jobs               = ["sphinx"]
          },
        ]
      }
    }

Description
===========

- **command** (str | required)

    The command and arguments separated by whitespaces.

- **logger** (:doc:`logger` | optional | default: ``{}``)

    The job logger configuration.

Jaffle Apps
===========

Only :doc:`WatchdogApp </apps/watchdog>` supports executing jobs.
