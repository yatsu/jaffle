# -*- coding: utf-8 -*-

from distutils.version import StrictVersion
import jupyter_client
from jupyter_client.ioloop.manager import IOLoopKernelManager
from traitlets import default


class TurretKernelManager(IOLoopKernelManager):

    @default('client_class')
    def _client_class_default(self):
        return 'turret.kernel_client.TurretKernelClient'

    def get_connection_info(self, session=False):
        info = super().get_connection_info(session=session)

        if StrictVersion(jupyter_client.__version__) < StrictVersion('5.1.0'):
            if session:
                # add *clone* of my session,
                # so that state such as digest_history is not shared.
                info['session'] = self._session_clone(self.session)

        return info

    def _session_clone(self, session):
        # make a copy
        new_session = type(session)()
        for name in session.traits():
            setattr(new_session, name, getattr(session, name))
        # fork digest_history
        new_session.digest_history = set()
        new_session.digest_history.update(session.digest_history)
        return new_session
