======
logger
======

The ``logger`` block configures log suppressing and replacing rules by regular expressions. ``logger`` is available in the root, ``app`` and ``process`` blocks. The root ``logger`` configures the global rules which are applied after each app- or process-level rule.

Example
=======

.. code-block:: hcl

    logger {
      suppress_regex = ["^\\s*$"] # drop empty line
      replace_regex = [
        {
          from = "(some_keyword)"
          to   = "\033[31m\\1\033[0m" # red color
        },
      ]
    }

Description
===========

- **name** (str | optional | default: <object name>)

    The logger name. The root ``logger`` does not have this.

    .. note::

       Each logger should have a unique logger name. If multiple loggers of apps, process or jobs have the same logger name, ``level``, ``suppress_regex``, etc. are overwritten multiple times and the last configuration takes effect. That may not be the expected behavior.

- **level** (str | optional | default: ``'info'``)

    The logger level. Log messages are filtered by this level. Available levels are 'critical', 'error', 'warning', 'info' and 'debug'. See Python ``logging`` reference for more information.

- **suppress_regex** ([str] | optional | default: ``[]``)

    Regular expression patterns to suppress log messages. If one of the patterns matches the log message, the message will be omitted.

- **replace_regex** ([{"from": str, "to": str}] | optional | default: ``[]``)

    The matched groups can be used in ``to`` string as ``\\1``, ``\\2``, and so on. Note that ``\`` (backslash) must be escaped by an extra ``\``, such as ``\\n``.

    .. tip::

       ``replace_regex`` is especially useful to emphasize keywords on debugging like the example below.
