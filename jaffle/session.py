# -*- coding: utf-8 -*-

from notebook.services.sessions.sessionmanager import SessionManager
from tornado import gen


class JaffleSessionManager(SessionManager):
    """
    Session manager for Jaffle.
    It extends Jupyter Notebook's SessionManager to pass additional arguments
    to ``create_session()`` and ``start_kernel_for_session()``.
    """

    @gen.coroutine
    def create_session(self, path=None, name=None, type=None, kernel_name=None, kernel_id=None,
                       **kwargs):
        """
        Creates a session and returns its model.

        This method overwrites ``SessionManager.create_session()`` to pass kwargs
        (e.g. ``env={...}``).

        Parameters
        ----------
        path : str
            the path for the given session
        name: str
            the name of the session
        type: string
            the type of the session
        kernel_name : str
            The name identifying which kernel spec to launch.
        kernel_id : str
            UUID for the kernel associated with this session
        kwargs : dict
            Additional arguments for a kernel.

        Returns
        -------
        session : dict
            Jupyter session model.
            (It is not a Jaffle session.)
        """
        session_id = self.new_session_id()
        if kernel_id is not None and kernel_id in self.kernel_manager:
            pass
        else:
            kernel_id = yield self.start_kernel_for_session(
                session_id, path, name, type, kernel_name, **kwargs
            )
        result = yield gen.maybe_future(
            self.save_session(session_id, path=path, name=name, type=type, kernel_id=kernel_id)
        )
        return result

    @gen.coroutine
    def start_kernel_for_session(self, session_id, path, name, type, kernel_name, **kwargs):
        """
        Starts a new kernel for a given Jupyter session.

        This method overwrites ``SessionManager.start_kernel_for_session()`` to pass kwargs
        (e.g. ``env={...}``).

        Parameters
        ----------
        session_id : str
            UUID for the Jupyter session.
        path : str
            The path for the given session.
        name: str
            The name of the session.
        type: string
            The type of the session.
        kernel_name : str
            The name identifying which kernel spec to launch.
        kwargs : dict
            Additional arguments for a kernel.

        Returns
        -------
        kernel_id : str
            UUID for the kernel associated with this session
        """
        kernel_path = self.contents_manager.get_kernel_path(path=path)
        kernel_id = yield gen.maybe_future(
            self.kernel_manager.start_kernel(path=kernel_path, kernel_name=kernel_name, **kwargs)
        )
        return kernel_id
