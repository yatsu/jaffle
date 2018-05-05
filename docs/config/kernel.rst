======
kernel
======

Example
=======

The ``kernel`` block defines a kernel instance name and configures the kernel.

.. code-block:: hcl

    kernel "py_kernel" {
      kernel_name = "python3"
      pass_env = ["PATH", "HOME"]
    }

Description
===========

- **kernel_name** (str | optional | default: ``""``)

    ``kernel_name`` is a Jupyter kernel name. You can install multiple kernels and switch them by specifying ``kernel_name``. If it is not specified, the default kernel will be launched. The kernel must be `IPython kernel`_ and the Python version must be greater than or equal to 3.4. See also `Installing the IPython kernel`_ in the IPython document.

    .. _IPython kernel: https://github.com/ipython/ipykernel
    .. _Installing the IPython kernel: https://ipython.readthedocs.io/en/stable/install/kernel_install.html

.. _pass_env:

- **pass_env** ([str] | optional | default: [])

    ``pass_env`` defines environment variables which will be passed to the kernel. Jaffle itself has the environment variables defined in your environment, but the kernel will be launched as an independent process and the environment variables are not passed by default.

    .. tip::

       If the kernel executes a Python console script in a virtualenv, you will have to pass ``PATH`` environment variable to the kernel.
