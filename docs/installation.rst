============
Installation
============

Prerequisite
============

- UNIX-like OS
    - Windows is not supported
- Python >= 3.4
- Jupyter Notebook >= 5.0

Turret also requires other libraries listed in `requirements.in`. They are automatically installed by the installer.

Installation
============

Please install as follows until the first release:

.. code-block:: sh

    $ git clone https://github.com/yatsu/turret
    $ cd turret
    $ python setup.py install

You will also probably need pytest:

.. code-block:: sh

    $ pip install watchdog pytest
