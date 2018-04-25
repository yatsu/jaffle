===
app
===

The ``app`` block configures a :doc:`Turret app </apps/index>` which will be launched in a kernel.

Example
=======

.. code-block:: hcl

    app "pytest" {
      class  = "turret.app.pytest.PyTestRunnerApp"
      kernel = "py_kernel"

      options {
        args = ["-s", "-v", "--color=yes"]

        auto_test = [
          "my_module/tests/test_*.py",
        ]

        auto_test_map {
          "my_module/**/*.py" = "my_module/tests/{}/test_{}.py"
        }
      }
    }

Description
===========

- **class** (str | required)

    The class name of the Turret app. It must begin with the top-level module name.
    e.g.: ``"turret.app.pytest.PyTestRunnerApp"``.

- **kernel** (str | required)

    The kernel in which the app is instantiated.
    The specified kernel must be defined in a :doc:`kernel` block.

- **start** (str | optional | default: ``null``)

    Python code to be executed just after the app is instanticated in a kernel.

- **logger** (:doc:`logger` | optional | default: ``{}``)

    The app logger configuration.

.. _app_options:

- **options** (map | optional | default: ``{}``)

    ``options`` will be passed to the app initializer (``__init__()`` method) as keyword arguments. The format of ``options`` depends on the app.