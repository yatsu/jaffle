# -*- coding: utf-8 -*-

from functools import wraps
from unittest.mock import patch


def clear_module_cache_once(method):
    """
    Decorator for a Jaffle app method to ensure clearing module cache only
    once. You can call ``BaseJaffleApp.clear_module_cache()`` multiple times
    without worrying about aduplicated cache clear.

    Parameters
    ----------
    method : function
        Method to be wrapped.

    Returns
    -------
    method : function
        Wrapped method.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        cleared = False
        __clear_module_cache = self.clear_module_cache

        def _clear_module_cache(modules):
            nonlocal cleared
            if cleared:
                return
            __clear_module_cache(modules)
            cleared = True

        with patch.object(self, 'clear_module_cache', _clear_module_cache):
            return method(self, *args, **kwargs)

    return wrapper
