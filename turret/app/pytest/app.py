# -*- coding: utf-8 -*-

from ..base import BaseTurretApp


class PyTestRunnerApp(BaseTurretApp):

    def run(self, watchdog_event):
        self.log.debug('event: %s', watchdog_event)
