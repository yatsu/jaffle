# -*- coding: utf-8 -*-

import os
import shlex
import subprocess
from tornado.escape import to_unicode
from ..display import Color, foreground_color, background_color, display_reset


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


functions = [env, exec, fg, bg, reset]
