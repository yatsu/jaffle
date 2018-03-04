# -*- coding: utf-8 -*-

from functools import wraps
import logging
import sys
from tornado import gen
from unittest.mock import patch
import zmq
from ...status import TurretStatus
from .logging import TurretAppLogHandler


class BaseTurretApp(object):
    """
    Base class for Turret apps.
    """

    completer_class = None

    lexer_class = None

    def __init__(self, app_name, turret_conf, turret_port, turret_status):
        """
        Initializes BaseTurretApp.

        Parameters
        ----------
        app_name : str
            App name defined in turret.hcl.
        turret_conf : dict
            Turret conf constructed from turret.hcl.
        turret_port : int
            TCP port for Turret ZMQ channel.
        turret_status : dict
            Turret status.
        """
        self.app_name = app_name
        self.turret_port = turret_port
        self.turret_conf = turret_conf
        self.turret_status = TurretStatus.from_dict(turret_status)
        self.ipython = get_ipython()  # noqa

        ctx = zmq.Context.instance()
        self.turret_socket = ctx.socket(zmq.PUSH)
        self.turret_socket.connect('tcp://127.0.0.1:{0}'.format(self.turret_port))

        self.log = logging.getLogger(app_name)
        level = turret_conf['app'][app_name].get('logger', {}).get('level', 'info')
        self.log.setLevel(getattr(logging, level.upper()))
        handler = TurretAppLogHandler(app_name, self.turret_socket)
        self.log.addHandler(handler)

    def execute(self, code, *args, **kwargs):
        """
        Parameters
        ----------
        code : str
            Code to be executed.
            It will be formateed as ``code.format(*args, **kwargs)``.
        args : list
            Positional arguments to ``code.format()``.
        kwargs : dict
            Keyward arguments to ``code.formmat()``.

        Returns
        -------
        future : tornado.gen.Future
            Future which will have the execution result.
        """
        future = gen.Future()
        result = self.ipython.run_cell(code.format(*args, **kwargs))
        future.set_result(result.result)
        return future

    def uncache_modules(self, modules):
        """
        Uncache modules.
        This method deletes cache of imported modules from ``sys.modules``
        whose name starts with specified modules.
        For example, ``turret`` is specified, ``turret.app`` will also be
        deleted.

        Parameters
        ----------
        modules : str[list]
            List of module (dot separated module names).
        """
        def match(mod):
            return any([mod == m or mod.startswith('{}.'.format(m)) for m in modules])

        for mod in [mod for mod in sys.modules if match(mod)]:
            self.log.debug('uncache: %s', mod)
            del sys.modules[mod]

    @classmethod
    def command_to_code(self, app_name, command):
        """
        Converts a command comes from ``turret attach <app>`` to a code to be
        executed.

        If the app supports ``turret attach``, this method must be implemented.

        Parameters
        ----------
        app_name : str
            App name defined in turret.hcl.
        command : str
            Command name received from the shell of ``turret attach``.

        Returns
        -------
        code : str
            Code to be executed.
        """
        raise NotImplementedError('Must be implemented to support attaching')


def uncache_modules_once(func):
    """
    Decorator to ensure doing uncache only once.
    You can call ``uncache_modules()`` multiple times without considering
    duplicated uncache and reloading in a method decorated by this.

    Parameters
    ----------
    func : function
        Function to be wrapped.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        uncached = False
        __uncache_modules = self.uncache_modules

        def _uncache_modules(modules):
            nonlocal uncached
            if uncached:
                return
            __uncache_modules(modules)
            uncached = True

        with patch.object(self, 'uncache_modules', _uncache_modules):
            return func(self, *args, **kwargs)

    return wrapper
