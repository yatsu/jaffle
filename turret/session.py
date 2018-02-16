# -*- coding: utf-8 -*-

from notebook.services.sessions.sessionmanager import SessionManager
from tornado import gen


class TurretSessionManager(SessionManager):

    @gen.coroutine
    def create_session(self, path=None, name=None, type=None, kernel_name=None, kernel_id=None,
                       **kwargs):
        """
        Creates a session and returns its model.

        This method overwrites ``SessionManager.create_session()`` to pass kwargs.
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
        Starts a new kernel for a given session.

        This method overwrites ``SessionManager.start_kernel_for_session()`` to pass kwargs.
        """
        kernel_path = self.contents_manager.get_kernel_path(path=path)
        kernel_id = yield gen.maybe_future(
            self.kernel_manager.start_kernel(path=kernel_path, kernel_name=kernel_name, **kwargs)
        )
        return kernel_id
