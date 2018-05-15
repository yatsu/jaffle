# -*- coding: utf-8 -*-

from ...config import ConfigDict
from ...functions import functions
from ...variables import VariablesNamespace


class AppConfig(object):
    """
    App configuration.
    """

    def __init__(self, app_name, conf, raw_namespace, runtime_variables, variables_conf,
                 jaffle_port, jobs_conf):
        """
        Initializes AppConfig.

        Parameters
        ----------
        app_name : str
            App name.
        conf : ConfigDict
            App-specific config.
        raw_namespace : dict
            Raw namespace for string interpolation.
        runtime_variables : dict
            Runtime variables.
        variables_conf : dict
            Variables config.
        jaffle_port : int
            Jaffle port.
        jobs_conf : ConfigDict
            Jobs config.
        """
        namespace = dict(
            raw_namespace,
            var=VariablesNamespace(variables_conf, vars=runtime_variables),
            **{f.__name__: f for f in functions}
        )

        self.app_name = app_name
        self.conf = ConfigDict(conf, namespace)
        self.raw_namespace = raw_namespace
        self.runtime_variables = runtime_variables
        self.jaffle_port = jaffle_port
        self.jobs_conf = ConfigDict(jobs_conf, namespace)
        self.variables_conf = variables_conf

    def __repr__(self):
        """
        Returns the string representation of AppConfig.

        Returns
        -------
        repr : str
            String representation of AppConfig.
        """
        return repr(self.to_dict())

    def to_dict(self):
        """
        Returns the dict representation of AppConfig.

        Returns
        -------
        data : dict
            Dict representation of AppConfig.
        """
        return dict(self.__dict__, conf=self.conf.raw(), jobs_conf=self.jobs_conf.raw())

    @classmethod
    def from_dict(cls, data):
        """
        Constructs AppConfig from a dict.

        Parameters
        ----------
        data : dict
            Dict object to construct AppConfig.
        """
        return cls(**data)
