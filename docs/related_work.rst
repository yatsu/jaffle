============
Related Work
============

Watchdog_
    Python API and shell utilities to monitor file system events. Jaffle depends on it.

pytest-testmon_
    pytest plugin to select tests affected by recent changes. It looks code coverage to determine which tests should be executed, whereas Jaffle uses simple pattern mapping.

pytest-watch_
    Continuous pytest runner using Watchdog, which also supports notification, before/after hoooks and using a custom runner script. It executes pytest as a subprocess.

Foreman_
    Procfile-based process manager.

coloredlogcat_py_ and pid_cat_
    Android logcat modifier. Jaffle's log formatter was inspired by them.

.. _Watchdog: https://github.com/gorakhargosh/watchdog
.. _pytest-testmon: https://github.com/tarpas/pytest-testmon
.. _pytest-watch: https://github.com/joeyespo/pytest-watch
.. _Foreman: https://github.com/ddollar/foreman
.. _coloredlogcat_py: http://jsharkey.org/logcat/
.. _pid_cat: https://github.com/JakeWharton/pidcat
