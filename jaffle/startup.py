# -*- coding: utf-8 -*-

from IPython.core.autocall import IPyAutocall


exit_org = exit


class Exit(IPyAutocall):
    """
    Overwrites ``exit`` and ``quit`` in a shell to keep kernel alive.
    """
    def __call__(self):
        exit_org(keep_kernel=True)


quit = exit = Exit()
