Sphinx Document Build Example
=============================

.. code-block:: hcl

    kernel "py_kernel" {
      pass_env = ["PATH"]
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
            patterns = [
              "*/turret/_version.py",
              "*/turret/app/*.py",
              "*/docs/*.*",
            ]

            ignore_patterns    = ["*/_build/*"]
            ignore_directories = true
            throttle           = 0.5

            jobs = [
              "sphinx",
            ]
          },
        ]
      }
    }

    job "sphinx" {
      command = "sphinx-build -M html docs docs/_build"
    }
