# -*- coding: utf-8 -*-

import json
import os
import pyjq
import shlex
import subprocess
from tornado.escape import to_unicode
import yaml
from .display import Color, foreground_color, background_color, display_reset


_COLOR_MAP = {c.name.lower(): c for c in Color}


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


def fg(color):
    """
    Inserts the escape sequence of the foreground color.

    Available colors are 'black', 'red', 'green', 'yellow', 'blue', 'magenta',
    'cyan', 'white', 'bright_black', 'bright_red', 'bright_green',
    'bright_yellow', 'bright_blue' , 'bright_magenta', 'bright_cyan' and
    'bright_white'.

    Parameters
    ----------
    color : str
        Foreground color in str (e.g. 'red').

    Returns
    -------
    seq : str
        Escape sequence of the foreground color.

    Raises
    ------
    ValueError
        Invalid color name.
    """
    try:
        return foreground_color(_COLOR_MAP[color])
    except KeyError:
        return ValueError('Invalid color {!r}'.format(color))


def bg(color):
    """
    Inserts the escape sequence of the background color.

    Available colors are 'black', 'red', 'green', 'yellow', 'blue', 'magenta',
    'cyan', 'white', 'bright_black', 'bright_red', 'bright_green',
    'bright_yellow', 'bright_blue' , 'bright_magenta', 'bright_cyan' and
    'bright_white'.

    Parameters
    ----------
    color : str
        Background color in str (e.g. 'red').

    Returns
    -------
    seq : str
        Escape sequence of the background color.

    Raises
    ------
    ValueError
        Invalid color name.
    """
    try:
        return background_color(_COLOR_MAP[color])
    except KeyError:
        return ValueError('Invalid color {!r}'.format(color))


def reset():
    """
    Inserts the escape sequence of display reeet.

    Returns
    -------
    seq : str
        Escape sequence of display reeet.
    """
    return display_reset()


def jq_all(query, data_str, *args, **kwargs):
    """
    Queries the nested data and returns all results as a list.

    Parameters
    ----------
    data_str : str
        Nested data in Python dict's representation format.
        If must be loadable by ``yaml.safe_load()``.

    Returns
    -------
    result : str
        String representation of the result list.
    """
    try:
        return json.dumps(pyjq.all(query, yaml.loads(data_str)), *args, **kwargs)
    except Exception as e:
        return 'jq error: {} query: {!r} str: {!r}'.format(e, query, data_str)


def jq_first(query, data_str, *args, **kwargs):
    """
    Queries the nested data and returns the first result.

    Parameters
    ----------
    data_str : str
        Nested data in Python dict's representation format.
        If must be loadable by ``yaml.safe_load()``.

    Returns
    -------
    result : str
        String representation of the result object.
    """
    try:
        return json.dumps(pyjq.first(query, yaml.safe_load(data_str)), *args, **kwargs)
    except Exception as e:
        return 'jq error: {} query: {!r} str: {!r}'.format(e, query, data_str)


def jq(query, data_str, *args, **kwargs):
    return jq_all(query, data_str, *args, **kwargs)


jq.__doc__ = jq_all.__doc__


def jqf(query, data_str, *args, **kwargs):
    return jq_first(query, data_str, *args, **kwargs)


jqf.__doc__ = jq_first.__doc__


functions = [env, exec, fg, bg, reset, jq_all, jq_first, jq, jqf]
