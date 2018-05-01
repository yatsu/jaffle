===============
jaffle.app.base
===============

.. module:: jaffle.app.base

.. _base_jaffle_app:

BaseJaffleApp
=============

.. autoclass:: BaseJaffleApp
   :members: execute_code, execute_command, execute_job, invalidate_module_cache, command_to_code

   .. attribute:: completer_class

      The completer class for the interactive shell.
      It is required only if the app supports interactive shell.

   .. attribute:: lexer_class

      The lexer class for the interactive shell.
      It is required only if the app supports interactive shell.

Utility Functions
=================

.. autofunction:: capture_method_output

.. autofunction:: invalidate_module_cache_once
