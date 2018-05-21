===============
Version History
===============

0.2.2 (May 21, 2018)
====================

- Fix: String interpolations in logger settings are not evaluated

0.2.1 (May 20, 2018)
====================

- Fix: String interpolations in app options are not evaluated

0.2.0 (May 16, 2018)
====================

- Now String interpolations are evaluated at runtime instead of on loading the configuration
- Add functions ``jq_all()`` and ``jq_first()`` and their aliases ``jq()`` and ``jqf()``
- Change environment variable prefix ``T_VAR_`` to ``J_VAR_``
- Simplify ``BaseJaffleApp`` I/F
- Improve Tornado app stability on syntax errors and exceptions raised in ``start()``
- Fix hidden Tornado log messages

0.1.2 (May 8, 2018)
===================

- Add ``fg()``, ``bg()`` and ``reset()`` function
- Fix errors on starting/stopping threaded Tornado app

0.1.0 (May 6, 2018)
===================

- Initial release
