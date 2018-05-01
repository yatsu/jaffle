=======
process
=======

The ``process`` block configures an external process. The output to ``stdout`` and ``stderr`` are redirected to the logger with level ``info`` and ``warning`` respectively.

Example
=======

.. code-block:: hcl

    process "webdev" {
      command = "yarn start"
      tty     = true

      env {
        BROWSER = "none"
      }
    }

Description
===========

- **command** (str | required)

    The command and arguments separated by whitespaces.

- **tty** (bool | optional | default: ``false``)

    Whether to enable special care for a TTY application. Some applications require a foreground TTY access and/or send escape sequences aggressively. When ``tty`` is true, Jaffle runs the process via `Pexpect`_ and filters the output. Font style sequences are still available but all other escape sequences will be dropped. Try this option if your command does not work or makes the log output collapse.

    .. _Pexpect: https://pexpect.readthedocs.io/en/stable/

- **env** (map | optional | default: ``{}``)

    The environment variables to be passed to the process.

- **logger** (:doc:`logger` | optional | default: ``{}``)

    The process logger configuration.
