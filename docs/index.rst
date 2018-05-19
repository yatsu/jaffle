================
Jaffle |version|
================

Jaffle is an automation tool for Python software development, which has the following features:

- Instantiate Python applications in a Jupyter_ kernel and allows them to interact each other
- Launch external processes
- Combine all log messages and allows filtering and reformatting by regular expressions and functions
- Built-in :doc:`WatchdogApp </apps/watchdog>` watches filesystem events and triggers another app, arbitrary code, and functions, which make it possible to setup various automations.

.. _Jupyter: https://jupyter.org/

Screenshot
==========

.. figure:: cookbook/tornado_example.gif
   :align: center

   Developing a single-page web app using Tornado_ and React_

.. _Tornado: http://www.tornadoweb.org/
.. _React: https://reactjs.org/

.. warning::

   Jaffle is intended to be a development tool and does not care much about security. Arbitrary Python code can be executed in ``jaffle.hcl`` and you should not use it as a part of production environment. ``jaffle.hcl`` is like a Makefile or a shell script included in a source code repository.

.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   installation
   commands/index
   config/index
   apps/index
   cookbook/index
   troubleshooting
   version_history
   related_work

.. toctree::
   :maxdepth: 2
   :caption: Developer Documentation

   devel/index
   api/index

Source Code
===========

GitHub repository: `yatsu/jaffle`_

.. _`yatsu/jaffle`: https://github.com/yatsu/jaffle

Bugs/Requests
=============

Please use the `GitHub issue tracker`_ to submit bugs or request features.

.. _`GitHub issue tracker`: https://github.com/yatsu/jaffle/issues

License
=======

Jaffle is available under `BSD 3-Clause License`_.

.. _`BSD 3-Clause License`: https://github.com/yatsu/jaffle/blob/master/LICENSE

This web site and all documentation are licensed under `Creative Commons 3.0`_.

.. _`Creative Commons 3.0`: https://creativecommons.org/licenses/by/3.0/

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
