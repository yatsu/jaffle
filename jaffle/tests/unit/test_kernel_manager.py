# -*- coding: utf-8 -*-

from jupyter_client.client import KernelClient

from jaffle.kernel_client import JaffleKernelClient
from jaffle.kernel_manager import JaffleKernelManager


class Foo(KernelClient):
    pass


def test_kernel_manager():
    km = JaffleKernelManager()
    km.is_ready is False
    km.client_class is JaffleKernelClient

    km = JaffleKernelManager(
        is_ready=True, client_class='jaffle.tests.unit.test_kernel_manager.Foo'
    )
    km.is_ready is False
    km.client_class is Foo
