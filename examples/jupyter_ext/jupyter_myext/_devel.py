# -*- coding: utf-8 -*-

from notebook.nbextensions import install_nbextension_python
from turret.app.base import BaseTurretApp, capture_method_output


class NBExtensionInstaller(BaseTurretApp):

    @capture_method_output
    def handle_watchdog_event(self, event):
        """
        This is same as ``jupyter nbextension install --user --py --overwrite jupyter_myext``.
        """
        self.log.info('Installing nbextension')
        install_nbextension_python('jupyter_myext', overwrite=True, user=True)
