# -*- coding: utf-8 -*-

from distutils.version import StrictVersion
import jupyter_client
from jupyter_client.ioloop.manager import IOLoopKernelManager
from traitlets import default, Bool


class JaffleKernelManager(IOLoopKernelManager):
    """
    Jupyter kernel manager for Jaffle server, which has a custom kernel client
    for error logging.

    If jupyter_client version is smaller than 5.1.0, it clones the session
    to avoid duplicated digest error on getting the connection info.
    """

    is_ready = Bool(False)

    @default('client_class')
    def _client_class_default(self):
        return 'jaffle.kernel_client.JaffleKernelClient'

    def get_connection_info(self, session=False):  # pragma: no cover
        """
        Gets the connection info as a dict

        If jupyter_client version is smaller than 5.1.0, this method clones the
        session to avoid duplicated digest error.

        Parameters
        ----------
        session : bool [default: False]
            If True, return our session object will be included in the
            connection info.
            If False (default), the configuration parameters of our session
            object will be included, rather than the session object itself.

        Returns
        -------
        connect_info : dict
            dictionary of connection information.
        """
        info = super().get_connection_info(session=session)

        if StrictVersion(jupyter_client.__version__) < StrictVersion('5.1.0'):
            if session:
                # add *clone* of my session,
                # so that state such as digest_history is not shared.
                info['session'] = self._session_clone(self.session)

        return info

    def _session_clone(self, session):  # pragma: no cover
        """
        Clones the Jupyter client session.

        Parameters
        ----------
        session : jupyter_client.session.Session
            Jupyter client session.

        Return
        ------
        new_session : jupyter_client.session.Session
            Cloned Jupyter client session.
        """
        # make a copy
        new_session = type(session)()
        for name in session.traits():
            setattr(new_session, name, getattr(session, name))
        # fork digest_history
        new_session.digest_history = set()
        new_session.digest_history.update(session.digest_history)
        return new_session
