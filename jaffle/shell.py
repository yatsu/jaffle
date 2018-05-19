# -*- coding: utf-8 -*-

from distutils.version import StrictVersion
import jupyter_console
from jupyter_console.ptshell import ZMQTerminalInteractiveShell


class JaffleInteractiveShell(ZMQTerminalInteractiveShell):  # pragma: no cover
    """
    Base interactive shell class for Jaffle.

    This class extends ``mainloop`` of ZMQTerminalInteractiveShell to prevent
    unexpected kernel shutdown on ``Ctrl-D``.
    """

    own_kernel = False

    def mainloop(self):
        """
        This method overwrites ZMQTerminalInteractiveShell.mainloop() to keep kernel alive
        on Ctrl-D exit.
        https://github.com/jupyter/jupyter_console/commit/120396382ee9e0e73b932c7bacb98df2c27b8313

        This is not required on jupyter_console >= 5.2
        """
        if StrictVersion(jupyter_console.__version__) < StrictVersion('5.2.0'):  # pragma: nocover
            # self.keepkernel = True
            self.keepkernel = not self.own_kernel  # keep kernel alive on Ctrl-D exit
            # An extra layer of protection in case someone mashing Ctrl-C breaks
            # out of our internal code.
            while True:
                try:
                    self.interact()
                    break
                except KeyboardInterrupt:
                    print("\nKeyboardInterrupt escaped interact()\n")

            if self._eventloop:
                self._eventloop.close()
            if self.keepkernel and not self.own_kernel:
                print('keeping kernel alive')
            elif self.keepkernel and self.own_kernel:
                print("owning kernel, cannot keep it alive")
                self.client.shutdown()
            else:
                print("Shutting down kernel")
                self.client.shutdown()
        else:
            super().mainloop()
