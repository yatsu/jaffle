====================
Interpolation Syntax
====================

Turret configuration supports interpolation syntax wrapped by ``${}``.
You can get :ref:`environment varialbes <env-vars>`, call :ref:`functions <functions>`, and execute Python code in it:

Example:

.. code-block:: sh

   ${'hello'.upper()}

The above produces ``'HELLO'``.

.. _env-vars:

Environment Variables
=====================

All environment variables consist of alphanumeric uppercase characters are available in the interpolation syntax.

Example:

.. code-block:: sh

   ${HOME}/etc

The above produces ``/home/your_account/etc`` if your ``HOME`` is ``'/home/your_account'``.

If you need a default value for an environment variable, use :ref:`env() <env>` function instead.

.. _functions:

Functions
=========

.. currentmodule:: turret.command.functions

.. _env:

env()
-----

.. autofunction:: env

exec()
------

.. autofunction:: exec

Filters
=======

The ``|`` operator can be used in a ``${}`` expression to apply filters.

Example:

.. code-block:: sh

   ${'hello world' | u}

The ``u`` filter applies URL escaping to the string, and produces ``'hello+world'``.

To apply more than one filter, separate them by a comma:

.. code-block:: sh

   ${'  hello world  ' | trim,u}

The above produces ``'hello+world'``.

Available Filters
-----------------

u
    URL escaping.

    ``${"hello <b>world</b>" | x}`` => ``'hello+world'``

h
    HTML escaping.

    ``${"hello <b>world</b>" | x}`` => ``'hello &lt;b&gt;world&lt;/b&gt;'``

x
    XML escaping.

    ``${"hello <b>world</b>" | x}`` => ``'hello &lt;b&gt;world&lt;/b&gt;'``

trim
    Whitespace trimming.

    ``${"  hello world  " | x}`` => ``'hello world'``

entity
    Produces HTML entity references for applicable strings.

    ``${"→" | entit}`` => ``'&rarr;'``