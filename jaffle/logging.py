# -*- coding: utf-8 -*-

import logging
from .display import Color, foreground_color, background_color, display_reset


class LogFormatter(logging.Formatter):
    """
    Log formatter for Python logging module.

    This formatter assigns a color to individual logger names.
    Note that it may overlap because the number of defined colors is only 6.

    The following additional variables are available n a format string to
    colorize the output.

    * ``time_color``
    * ``time_color_end``
    * ``name_color``
    * ``name_color_end``
    * ``level_color``
    * ``level_color_end``

    The typical log format string is:

    >>> ('%(time_color)s%(asctime)s.%(msecs).03d%(time_color_end)s '
    ...  '%(name_color)s%(name)14s%(name_color_end)s '
    ...  '%(level_color)s %(levelname)1.1s %(level_color_end)s %(message)s')
    """

    _NAME_COLOR_PAIRS = [
        (Color.CYAN, None),
        (Color.MAGENTA, None),
        (Color.YELLOW, None),
        (Color.GREEN, None),
        (Color.BLUE, None),
        (Color.RED, None)
    ]

    _LEVEL_COLOR_PAIRS = {
        logging.CRITICAL: (Color.BLACK, Color.RED),
        logging.ERROR: (Color.BLACK, Color.RED),
        logging.WARNING: (Color.BLACK, Color.YELLOW),
        logging.INFO: (Color.BLACK, Color.GREEN),
        logging.DEBUG: (Color.BLACK, Color.BLUE)
    }

    _TIME_COLOR_PAIR = (Color.WHITE, Color.BRIGHT_BLACK)

    def __init__(self, fmt=None, datefmt=None, style='%', enable_color=True):
        """
        Initialize the formatter with specified format strings.

        Parameters
        ----------
        fmt : str
            Format string.
        datefmt : str
            Date format.
        style : str
            Style parameter.
        enable_color : bool
            Whether to enable color output.
        """
        super().__init__(fmt, datefmt, style)

        self.enable_color = enable_color
        self.name_colors = {}

    def format(self, record):
        """
        Formats the log record as text.

        Parameters
        ----------
        record : logging.LogRecord
            Log record.

        Returns
        -------
        formatted : str
            Formatted text.
        """
        rec = logging.getLogRecordFactory()(level=record.levelno, **record.__dict__)

        try:
            rec.message = rec.getMessage()
        except Exception as e:
            rec.message = 'Bad message (%r): %r' % (e, rec.__dict__)

        rec.asctime = self.formatTime(rec, self.datefmt)

        rec.time_color = self._color_start(*self._TIME_COLOR_PAIR)
        rec.time_color_end = self._color_end()

        name_color_pair = self.name_colors.get(rec.name)
        if name_color_pair is None:
            name_color_pair = self._NAME_COLOR_PAIRS[
                len(self.name_colors) % len(self._NAME_COLOR_PAIRS)
            ]
            self.name_colors[rec.name] = name_color_pair
        rec.name_color = self._color_start(*name_color_pair)
        rec.name_color_end = self._color_end()

        rec.level_color = self._color_start(*self._LEVEL_COLOR_PAIRS[rec.levelno])
        rec.level_color_end = self._color_end()

        formatted = self._fmt % rec.__dict__

        if rec.exc_info:
            if not rec.exc_text:
                rec.exc_text = self.formatException(rec.exc_info)
        if rec.exc_text:
            formatted = '\n'.join([formatted.rstrip()] + rec.exc_text.split('\n'))

        return formatted.replace('\n', '\n    ')

    def _color_start(self, fg_color, bg_color=None):
        """
        Returns the beginning of a color sequence.

        Parameters
        ----------
        fg_color : Color
            Foreground color.
        bg_color : Color or None
            Background color.

        Returns
        -------
        seq : str
            The beginning of a color sequence.
        """
        if self.enable_color:
            return '{}{}'.format(
                foreground_color(fg_color),
                background_color(bg_color) if bg_color else ''
            )
        else:
            return ''

    def _color_end(self):
        """
        Returns the end of a color sequence.

        Parameters
        ----------
        color : Color
            Color.

        Returns
        -------
        seq : str
            The end of a color sequence.
        """
        if self.enable_color:
            return display_reset()
        else:
            return ''
