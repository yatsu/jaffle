# -*- coding: utf-8 -*-

import os
import shlex
import subprocess
from tornado.escape import to_unicode


def env(name, default=''):
    """
    Gets an environment variable.

    Parameters
    ----------
    name : str
        Environment variable name.
    default : str
        Default value.

    Returns
    -------
    env : str
        Value of the environment variable.
    """
    return os.environ.get(name, default)


def exec(command):
    """
    Executes a command and returns the result of it.

    Parameters
    ----------
    command : str
        Command name and arguments separated by whitespaces.

    Returns
    -------
    result : str
        Result of the command.
    """
    return to_unicode(subprocess.check_output(shlex.split(command)))


functions = [env, exec]
