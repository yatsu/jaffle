# -*- coding: utf-8 -*-

import logging


class LogFormatter(logging.Formatter):

    def format(self, record):
        colored_record = logging.getLogRecordFactory()(
            level=record.levelno, **record.__dict__
        )
        return super().format(colored_record)
