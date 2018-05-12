========
variable
========

The ``variable`` block defines a variable which will be used in another blocks. The variables can be set from environment variables (``J_VAR_name=value``) or the command argument (``--variables='["name=value"]'``).

Example
=======

.. code-block:: hcl

    variable "disable_frontend" {
      type = "bool"
      default = false
    }

    process "frontend" {
      command  = "yarn start"
      tty      = true
      disabled = "${var.disable_frontend}"
    }

Description
===========

- **type** (str | optional | default: undefined)

    The type of the variable. Available types are 'str', 'bool', 'int', 'float', 'list' and 'dict'.

- **default** (object | optional | default: undefined)

    The default value of the variable. If it is not defined, the value must be provided at runtime from an environment variable or the command-line argument.

If ``type`` is not provided, it will be inferred based on ``default``. If ``default`` is not provided, it is assumed to be ``str``.

Embedding Variables
===================

The variable embedding can be used only in a string:

.. code-block:: hcl

    disabled = "${var.disable_frontend}" # OK

It cannot be used outside of a string even though the target attribute requires bool or int because it is not a valid HCL_:

.. _HCL: https://github.com/hashicorp/hcl

.. code-block:: none

    disabled = ${var.disable_frontend} # NG

In Jaffle, the following strings can be treated as boolean values:

- ``'true'`` and ``'1'`` => ``true``
- ``'false'`` and ``'0'`` => ``false``

.. code-block:: hcl

    disabled = false

Setting Variables
=================

Your can set values to the variables from environment variables (``J_VAR_name=value``) or the command argument (``--variables='["name=value"]'``).

Example: Setting ``true`` to ``disable_frontend`` from an environment variable:

.. code-block:: sh

    $ J_VAR_disable_frontend=true jaffle start

Example: Setting ``true`` to ``disable_frontend`` from the command-line argument:

.. code-block:: sh

    $ jaffle start --variables='["disable_frontend=true"]'
