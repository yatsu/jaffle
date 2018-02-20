# -*- coding: utf-8 -*-

from jupyter_client.ioloop.manager import IOLoopKernelManager
from traitlets import default


class TurretKernelManager(IOLoopKernelManager):

    @default('client_class')
    def _client_class_default(self):
        return 'turret.kernel_client.TurretKernelClient'
