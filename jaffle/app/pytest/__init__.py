# -*- coding: utf-8 -*-

from _pytest import config


_create_terminal_writer_org = config.create_terminal_writer


def _create_terminal_writer(config, *args, **kwargs):
    tw = _create_terminal_writer_org(config, *args, **kwargs)
    tw.fullwidth -= 32
    return tw


# Patch create_terminal_writer() to shorten the screen width to fit the
# log message. This should be configurable...
setattr(config, 'create_terminal_writer', _create_terminal_writer)


from .app import PyTestRunnerApp  # noqa
