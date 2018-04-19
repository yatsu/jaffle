Sphinx Document Build Example
=============================

.. code-block:: hcl

    kernel "py_kernel" {
      pass_env = ["PATH"] # required to run sphinx-build in virtualenv
    }

    app "watchdog" {
      class  = "turret.app.watchdog.WatchdogApp"
      kernel = "py_kernel"

      logger {
        level = "info"
      }

      options {
        handlers = [
          {
            patterns           = ["*/docs/*.*"]
            ignore_patterns    = ["*/_build/*"]
            ignore_directories = true
            throttle           = 0.5
            jobs               = ["sphinx"]
          },
        ]
      }
    }

    job "sphinx" {
      command = "sphinx-build -M html docs docs/_build"
    }
