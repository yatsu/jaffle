# -*- coding: utf-8 -*-

from enum import Enum


_ESCSEQ_FMT = '\033[%dm'


class Color(Enum):
    """
    ANSI colors.
    """
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    BRIGHT_BLACK = 90
    BRIGHT_RED = 91
    BRIGHT_GREEN = 92
    BRIGHT_YELLOW = 93
    BRIGHT_BLUE = 94
    BRIGHT_MAGENTA = 95
    BRIGHT_CYAN = 96
    BRIGHT_WHITE = 97


def foreground_color(color):
    """
    Returns the escape sequence of the foreground color.

    Parameters
    ----------
    color : Color
        Foreground color.

    Returns
    -------
    seq : str
        Escape sequence of the foreground color.
    """
    return _ESCSEQ_FMT % color.value


def background_color(color):
    """
    Returns the escape sequence of the background color.

    Parameters
    ----------
    color : Color
        Background color.

    Returns
    -------
    seq : str
        Escape sequence of the background color.
    """
    return _ESCSEQ_FMT % (color.value + 10)


def display_reset():
    """
    Returns the escape sequence of display reeet.

    Returns
    -------
    seq : str
        Escape sequence of display reeet.
    """
    return _ESCSEQ_FMT % 0
