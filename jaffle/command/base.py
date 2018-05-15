# -*- coding: utf-8 -*-

from IPython.core import ultratb
import logging
import os
from pathlib import Path
import re
import sys
from traitlets.config.application import Application, catch_config_error
from traitlets import Bool, Dict, List, Unicode, default
from ..logging import LogFormatter
from ..variables import get_runtime_variables, VAR_PATTERN


aliases = {
    'log-level': 'Application.log_level',
    'log-datefmt': 'Application.log_datefmt',
    'log-format': 'Application.log_format',
    'runtime-dir': 'BaseJaffleCommand.runtime_dir'
}

flags = {
    'debug': (
        {'Application': {'log_level': logging.DEBUG}},
        'set log level to logging.DEBUG (maximize logging output)'
    ),
    'y': (
        {'BaseJaffleCommand': {'answer_yes': True}},
        'Answer yes to any questions instead of prompting.'
    ),
    'disable-color': (
        {'BaseJaffleCommand': {'color': False}},
        'Disable color output.'
    )
}


class BaseJaffleCommand(Application):
    """
    Base class for Jaffle commands.
    """
    _ENV_PATTERN = re.compile(r'^[A-Za-z0-9_]+')

    name = 'jaffle'
    description = 'Jaffle'

    aliases = aliases
    flags = flags

    _log_formatter_cls = LogFormatter

    @default('log')
    def _log_default(self):
        log = logging.getLogger('jaffle')
        log.setLevel(self.log_level)
        log.propagate = False
        formatter = self._log_formatter_cls(
            fmt=self.log_format,
            datefmt=self.log_datefmt,
            enable_color=self.color
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        log.addHandler(handler)
        return log

    @default('log_level')
    def _log_level_default(self):
        return logging.INFO

    @default('log_datefmt')
    def _default_log_datefmt(self):
        return "%H:%M:%S"

    @default('log_format')
    def _log_format_default(self):
        return '%(message)s'

    color = Bool(True, config=True, help='Enable color output.')

    def _color_changed(self):
        self.log.handlers[0].formatter.enable_color = self.color

    config_file = Unicode(config=True, help='Config file path.')

    answer_yes = Bool(False, config=True, help='Answer yes to any prompts.')

    runtime_dir = Unicode('.jaffle', config=True, help='Runtime directory path.')

    variables = List(Unicode(), default_value=[], config=True)

    raw_namespace = Dict({})

    runtime_variables = Dict({})

    @property
    def status_file_path(self):
        return Path(self.runtime_dir) / 'jaffle.json'

    def kernel_connection_file_path(self, kernel_id):
        return Path(self.runtime_dir) / 'kernel-{}.json'.format(kernel_id)

    @catch_config_error
    def initialize(self, argv=None):
        """
        Initializes BaseJaffleCommand.

        Parameters
        ----------
        argv : list[str]
            Command line strings.
        """
        super().initialize(argv)

        sys.excepthook = ultratb.ColorTB()

        self.raw_namespace = {k: v for k, v in os.environ.items()
                              if self._ENV_PATTERN.search(k)
                              and not VAR_PATTERN.search(k)}

        self.runtime_variables = get_runtime_variables(self.variables)
