# -*- coding: utf-8 -*-

from unittest.mock import patch
from jaffle.display import Color
from jaffle.functions import (
    _COLOR_MAP, env, exec, fg, bg, reset, jq_all, jq_first, jq, jqf, functions
)


def test_evn():
    with patch('jaffle.functions.os.environ', {'FOO': 'foo', 'BAR': 'bar'}):
        assert env('FOO') == 'foo'
        assert env('BAR', 'default') == 'bar'
        assert env('BAZ', 'default') == 'default'


def test_exec():
    with patch('jaffle.functions.to_unicode') as to_unicode:
        with patch('jaffle.functions.subprocess.check_output')as check_output:
            result = exec('hello --world')

    assert result is to_unicode.return_value
    to_unicode.assert_called_once_with(check_output.return_value)
    check_output.assert_called_once_with(['hello', '--world'])


def test_color():
    assert _COLOR_MAP == {
        'black': Color.BLACK,
        'red': Color.RED,
        'green': Color.GREEN,
        'yellow': Color.YELLOW,
        'blue': Color.BLUE,
        'magenta': Color.MAGENTA,
        'cyan': Color.CYAN,
        'white': Color.WHITE,
        'bright_black': Color.BRIGHT_BLACK,
        'bright_red': Color.BRIGHT_RED,
        'bright_green': Color.BRIGHT_GREEN,
        'bright_yellow': Color.BRIGHT_YELLOW,
        'bright_blue': Color.BRIGHT_BLUE,
        'bright_magenta': Color.BRIGHT_MAGENTA,
        'bright_cyan': Color.BRIGHT_CYAN,
        'bright_white': Color.BRIGHT_WHITE
    }


def test_fg():
    assert fg('black') == '\033[30m'
    assert fg('red') == '\033[31m'
    assert fg('green') == '\033[32m'
    assert fg('yellow') == '\033[33m'
    assert fg('blue') == '\033[34m'
    assert fg('magenta') == '\033[35m'
    assert fg('cyan') == '\033[36m'
    assert fg('white') == '\033[37m'
    assert fg('bright_black') == '\033[90m'
    assert fg('bright_red') == '\033[91m'
    assert fg('bright_green') == '\033[92m'
    assert fg('bright_yellow') == '\033[93m'
    assert fg('bright_blue') == '\033[94m'
    assert fg('bright_magenta') == '\033[95m'
    assert fg('bright_cyan') == '\033[96m'
    assert fg('bright_white') == '\033[97m'


def test_bg():
    assert bg('black') == '\033[40m'
    assert bg('red') == '\033[41m'
    assert bg('green') == '\033[42m'
    assert bg('yellow') == '\033[43m'
    assert bg('blue') == '\033[44m'
    assert bg('magenta') == '\033[45m'
    assert bg('cyan') == '\033[46m'
    assert bg('white') == '\033[47m'
    assert bg('bright_black') == '\033[100m'
    assert bg('bright_red') == '\033[101m'
    assert bg('bright_green') == '\033[102m'
    assert bg('bright_yellow') == '\033[103m'
    assert bg('bright_blue') == '\033[104m'
    assert bg('bright_magenta') == '\033[105m'
    assert bg('bright_cyan') == '\033[106m'
    assert bg('bright_white') == '\033[107m'


def test_reset():
    assert reset() == '\033[0m'


def test_functions():
    assert functions == [
        env, exec, fg, bg, reset, jq_all, jq_first, jq, jqf
    ]
