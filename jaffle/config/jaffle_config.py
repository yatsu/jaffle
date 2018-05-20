# -*- coding: utf-8 -*-

import hcl
from pathlib import Path
import re
from ..functions import functions
from ..utils import deep_merge
from ..variables import VariablesNamespace
from .value import ConfigValue


class JaffleConfig(object):
    """
    Jaffle configuration loaded from ``jaffle.hcl``.
    """

    def __init__(self, namespace, variable=None, kernel=None, app=None, process=None, job=None,
                 logger=None):
        """
        Initializes JaffleConfig.

        Parameters
        ----------
        namespace : dict
            Namespace for string interpolation.
        variable : dict
            Variables configuration.
        kernel : dict
            Kernel configuration.
        app : dict
            App configuration.
        process : dict
            Process configuration.
        job : dict
            Job configuration.
        logger : dict
            Logger configuration.
        """
        self.namespace = namespace
        self.variable = ConfigValue.create(variable or {}, namespace)
        self.kernel = ConfigValue.create(kernel or {}, namespace)
        self.app = ConfigValue.create(app or {}, namespace)
        self.process = ConfigValue.create(process or {}, namespace)
        self.job = ConfigValue.create(job or {}, namespace)
        self.logger = ConfigValue.create(logger or {}, namespace)

        self.app_log_suppress_patterns = {
            app_name: [re.compile(r) for r in
                       app_data.get('logger', {}).get('suppress_regex', [])]
            for app_name, app_data in self.app.items()
        }
        self.app_log_replace_patterns = {
            app_name: [(re.compile(r['from']), r['to']) for r in
                       app_data.get('logger', {}).get('replace_regex', [])]
            for app_name, app_data in self.app.items()
        }
        self.global_log_suppress_patterns = [
            re.compile(r)
            for r in self.logger.get('suppress_regex', default=[])
        ]
        self.global_log_replace_patterns = [
            (re.compile(r['from']), r['to'])
            for r in self.logger.get('replace_regex', default=[])
        ]

    def __repr__(self):
        """
        Returns string representation of JaffleConfig.

        Returns
        -------
        repr : str
            String representation of JaffleConfig.
        """
        return repr(self.raw())

    def raw(self):
        """
        Returns the raw contents of the configuration.

        Returns
        -------
        raw : dict
            Raw contents of the configuration.
        """
        return {
            'namespace': self.namespace,
            'variable': self.variable.raw(),
            'kernel': self.kernel.raw(),
            'app': self.app.raw(),
            'process': self.process.raw(),
            'job': self.job.raw(),
            'logger': self.logger.raw()
        }

    @classmethod
    def load(cls, file_paths, raw_namespace, runtime_variables):
        """
        Loads JaffleConfig from files with given namespace and variables.

        Parameters
        ----------
        file_paths : list[pathlib.Path]
            List of file paths.
        raw_namespace : dict
            Raw namespace for string interpolation.
        runtime_variables : dict
            Runtime variables.
        """
        return cls.create(deep_merge(*(cls._load_file(f) for f in file_paths)),
                          raw_namespace, runtime_variables)

    @classmethod
    def create(cls, data_dict, raw_namespace, runtime_variables):
        """
        Creates JaffleConfig from dict data, namespace and variables.

        Parameters
        ----------
        data_dict : dict
            Dict data loaded from config files.
        raw_namespace : dict
            Raw namespace for string interpolation.
        runtime_variables : dict
            Runtime variables.
        """
        namespace = dict(
            raw_namespace,
            var=VariablesNamespace(data_dict.get('variable', {}), vars=runtime_variables),
            **{f.__name__: f for f in functions}
        )
        return cls(namespace, **data_dict)

    @classmethod
    def _load_file(cls, file_path):
        """
        Loads config data from a file.

        Parameters
        ----------
        file_path : pathlib.Path or str
            File path.

        Returns
        -------
        data : dict
            Config data.
        """
        with Path(file_path).open() as f:
            return hcl.load(f)
