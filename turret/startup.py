# -*- coding: utf-8 -*-

from IPython.core.autocall import IPyAutocall


exit_org = exit


class Exit(IPyAutocall):

    def __call__(self):
        exit_org(True)


quit = exit = Exit()
