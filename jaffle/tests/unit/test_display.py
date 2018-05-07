# -*- coding: utf-8 -*-

from jaffle.display import Color, foreground_color, background_color, display_reset


def test_foreground_color():
    assert foreground_color(Color.BLACK) == '\033[30m'
    assert foreground_color(Color.RED) == '\033[31m'
    assert foreground_color(Color.GREEN) == '\033[32m'
    assert foreground_color(Color.YELLOW) == '\033[33m'
    assert foreground_color(Color.BLUE) == '\033[34m'
    assert foreground_color(Color.MAGENTA) == '\033[35m'
    assert foreground_color(Color.CYAN) == '\033[36m'
    assert foreground_color(Color.WHITE) == '\033[37m'
    assert foreground_color(Color.BRIGHT_BLACK) == '\033[90m'
    assert foreground_color(Color.BRIGHT_RED) == '\033[91m'
    assert foreground_color(Color.BRIGHT_GREEN) == '\033[92m'
    assert foreground_color(Color.BRIGHT_YELLOW) == '\033[93m'
    assert foreground_color(Color.BRIGHT_BLUE) == '\033[94m'
    assert foreground_color(Color.BRIGHT_MAGENTA) == '\033[95m'
    assert foreground_color(Color.BRIGHT_CYAN) == '\033[96m'
    assert foreground_color(Color.BRIGHT_WHITE) == '\033[97m'


def test_background_color():
    assert background_color(Color.BLACK) == '\033[40m'
    assert background_color(Color.RED) == '\033[41m'
    assert background_color(Color.GREEN) == '\033[42m'
    assert background_color(Color.YELLOW) == '\033[43m'
    assert background_color(Color.BLUE) == '\033[44m'
    assert background_color(Color.MAGENTA) == '\033[45m'
    assert background_color(Color.CYAN) == '\033[46m'
    assert background_color(Color.WHITE) == '\033[47m'
    assert background_color(Color.BRIGHT_BLACK) == '\033[100m'
    assert background_color(Color.BRIGHT_RED) == '\033[101m'
    assert background_color(Color.BRIGHT_GREEN) == '\033[102m'
    assert background_color(Color.BRIGHT_YELLOW) == '\033[103m'
    assert background_color(Color.BRIGHT_BLUE) == '\033[104m'
    assert background_color(Color.BRIGHT_MAGENTA) == '\033[105m'
    assert background_color(Color.BRIGHT_CYAN) == '\033[106m'
    assert background_color(Color.BRIGHT_WHITE) == '\033[107m'


def test_display_reset():
    assert display_reset() == '\033[0m'
