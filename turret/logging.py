# -*- coding: utf-8 -*-

from enum import Enum
import logging


Color = Enum('Color', 'BLACK RED GREEN YELLOW BLUE MAGENTA CYAN WHITE', start=0)


class LogFormatter(logging.Formatter):

    _COLOR_FMT = '\033[%sm'
    _COLOR_END = '\033[0m'

    _NAME_COLORS = [
        (Color.CYAN, None),
        (Color.MAGENTA, None),
        (Color.YELLOW, None),
        (Color.GREEN, None),
        (Color.BLUE, None),
        (Color.RED, None)
    ]

    _LEVEL_COLORS = {
        logging.CRITICAL: (Color.BLACK, Color.RED),
        logging.ERROR: (Color.BLACK, Color.RED),
        logging.WARNING: (Color.BLACK, Color.YELLOW),
        logging.INFO: (Color.BLACK, Color.GREEN),
        logging.DEBUG: (Color.BLACK, Color.BLUE)
    }

    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

        self.name_colors = {}
        self.last_name = None

    def format(self, record):
        rec = logging.getLogRecordFactory()(level=record.levelno, **record.__dict__)

        try:
            rec.message = rec.getMessage()
        except Exception as e:
            rec.message = 'Bad message (%r): %r' % (e, rec.__dict__)

        rec.asctime = self.formatTime(rec, self.datefmt)

        name_color = self.name_colors.get(rec.name)
        if name_color is None:
            name_color = self._NAME_COLORS[len(self.name_colors) % len(self._NAME_COLORS)]
            self.name_colors[rec.name] = name_color
        rec.name_color = self._COLOR_FMT % self._color(name_color)
        rec.name_color_end = self._COLOR_END

        rec.level_color = self._COLOR_FMT % self._color(self._LEVEL_COLORS[rec.levelno])
        rec.level_color_end = self._COLOR_END

        if rec.name == self.last_name:
            rec.name = ''
        else:
            self.last_name = rec.name

        formatted = self._fmt % rec.__dict__

        if rec.exc_info:
            if not rec.exc_text:
                rec.exc_text = self.formatException(rec.exc_info)
        if rec.exc_text:
            formatted = '\n'.join([formatted.rstrip()] + rec.exc_textx.split('\n'))

        return formatted.replace('\n', '\n    ')

    def _color(self, color):
        return ';'.join(
            [['3%d', '10%d'][i] % c.value for i, c in enumerate(color) if c is not None]
        )
