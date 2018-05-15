# -*- coding: utf-8 -*-

import json
import filelock
from pathlib import Path


class JaffleStatus(object):
    """
    Jaffle server status.
    """
    _LOCK_TIMEOUT = 5

    def __init__(self, pid, raw_namespace, runtime_variables, sessions=None, apps=None):
        """
        Initializes JaffleStatus.

        Parameters
        ----------
        pid : int
            Process ID.
        """
        self.pid = pid
        self.raw_namespace = raw_namespace
        self.runtime_variables = runtime_variables
        self.sessions = sessions or {}
        self.apps = apps or {}

    def __repr__(self):
        """
        Returns the string representation of JaffleStatus.

        Returns
        -------
        repr : str
            String representation of JaffleStatus.
        """
        return '<%s {pid: %d #sessions: %d #apps: %d}>' % (
            type(self).__name__, self.pid, len(self.sessions), len(self.apps))

    @classmethod
    def from_dict(cls, status_dict):
        """
        Creates a JaffleStatus from a dict.

        Parameters
        ----------
        status_dict : dict
            Python dict to initialize JaffleStatus.

        Returns
        -------
        status : JaffleStatus
            Jaffle server status.
        """
        return cls(
            pid=status_dict.get('pid'),
            raw_namespace=status_dict.get('raw_namespace', {}),
            runtime_variables=status_dict.get('runtime_variables', {}),
            sessions={n: JaffleSession.from_dict(s)
                      for n, s in status_dict.get('sessions', {}).items()},
            apps={n: JaffleAppData.from_dict(a)
                  for n, a in status_dict.get('apps', {}).items()}
        )

    def add_session(self, id, name, kernel=None):
        """
        Creates a Jaffle session and registers it to a JaffleStatus.

        Parameters
        ----------
        id : str
            Session ID (UUID).
        name : str
            Jaffle session name (= kernel instance name defined in jaffle.hcl).
        kernel : dict
            A dict of Kernel ID and name.
        """
        session = JaffleSession(id, name, kernel)
        self.sessions[session.name] = session

    def add_app(self, name, session_name, class_name, start, options):
        """
        Creates a Jaffle app data and registers it to a JaffleStatus.

        Parameters
        ----------
        name : str
            App name.
        session_name : str
            Jaffle session name (= kernel instance name defined in jaffle.hcl).
        class_name : str
            Class name of the app.
        start : str or None
            Start code of the app.
        options : dict
            Options for the app.
        """
        app = JaffleAppData(name, session_name, class_name, start, options)
        self.apps[app.name] = app

    def to_dict(self):
        """
        Returns the dict representation of a JaffleStatus.

        Returns
        -------
        status : dict
            Dict representation of a JaffleStatus.
        """
        return {
            'pid': self.pid,
            'raw_namespace': self.raw_namespace,
            'runtime_variables': self.runtime_variables,
            'sessions': {n: s.to_dict() for n, s in self.sessions.items()},
            'apps': {n: a.to_dict() for n, a in self.apps.items()}
        }

    @classmethod
    def load(cls, file_path):
        """
        Loads JaffleStatus from a file.

        Parameters
        ----------
        file_path : pathlib.Path or str
            File path.

        Returns
        -------
        status : JaffleStatus
            Jaffle server status.
        """
        with filelock.FileLock(str(file_path) + '.lock').acquire(timeout=cls._LOCK_TIMEOUT):
            with Path(file_path).open() as f:
                status_dict = json.load(f)
                return JaffleStatus.from_dict(status_dict)

    def save(self, file_path):
        """
        Saves JaffleStatus to a file.

        Parameters
        ----------
        file_path : pathlib.Path or str
            File path.
        """
        with filelock.FileLock(str(file_path) + '.lock').acquire(timeout=self._LOCK_TIMEOUT):
            with file_path.open('w') as f:
                json.dump(self.to_dict(), f, indent=2)

    def destroy(self, file_path):
        """
        Deletes the JaffleStatus file and the lock file of it.

        Parameters
        ----------
        file_path : pathlib.Path or str
            File path.
        """
        if file_path.exists():
            with filelock.FileLock(str(file_path) + '.lock').acquire(timeout=self._LOCK_TIMEOUT):
                file_path.unlink()


class JaffleSession(object):
    """
    Jaffle session.
    """

    def __init__(self, id, name, kernel=None):
        """
        Initializes JaffleSession.

        Parameters
        ----------
        id : str
            Session ID (UUID).
        name : str
            Jaffle session name (= kernel instance name defined in jaffle.hcl).
        kernel : dict or None
            A dict of Kernel ID and name.
        """
        self.id = id
        self.name = name
        self.kernel = JaffleKernelData.from_dict(kernel) if kernel else None

    def __repr__(self):
        """
        Returns the string representation of a JaffleSession.

        Returns
        -------
        repr : str
            String representation of a JaffleSession.
        """
        return '<%s {id: %s name: %s kernel: %s}>' % (
            self.__class__.__name__, self.id, self.name, self.kernel)

    @classmethod
    def from_dict(cls, data):
        """
        Creates a JaffleSession from a dict.

        Parameters
        ----------
        data : dict
            Python dict to initialize JaffleSession.

        Returns
        -------
        session : JaffleSession.
            Jaffle session.
        """
        return cls(id=data.get('id'), name=data.get('name'), kernel=data.get('kernel'))

    def to_dict(self):
        """
        Returns the dict representation of a JaffleSession.

        Returns
        -------
        session : dict
            Dict representation of a JaffleSession.
        """
        return {
            'id': self.id,
            'name': self.name,
            'kernel': self.kernel.to_dict()
        }


class JaffleKernelData(object):
    """
    Jaffle kernel data.
    """

    def __init__(self, id, name):
        """
        Initializes JaffleKernelData.

        Parameters
        ----------
        id : str
            Kernel ID (UUID).
        name : str
            kernel name (e.g. 'python3').
        """
        self.id = id
        self.name = name

    def __repr__(self):
        """
        Returns the string representation of a JaffleKernelData.

        Returns
        -------
        repr : str
            String representation of a JaffleKernelData.
        """
        return '<%s {id: %s name: %s}>' % (
            self.__class__.__name__, self.id, self.name)

    @classmethod
    def from_dict(cls, data):
        """
        Creates a JaffleKernelData from a dict.

        Parameters
        ----------
        data : dict
            Python dict to initialize JaffleKernelData.

        Returns
        -------
        kernel_data : JaffleKernelData.
            Kernel data.
        """
        return cls(**{a: data.get(a) for a in ['id', 'name']})

    def to_dict(self):
        """
        Returns the dict representation of a JaffleKernelData.

        Returns
        -------
        kernel_data : dict
            Dict representation of a JaffleKernelData.
        """
        return {
            'id': self.id,
            'name': self.name
        }


class JaffleAppData(object):
    """
    Jaffle app data.
    """

    def __init__(self, name, session_name, class_name, start, options):
        """
        Initializes JaffleAppData.

        Parameters
        ----------
        name : str
            App name.
        session_name : str
            Jaffle session name (= kernel instance name defined in jaffle.hcl).
        class_name : str
            Class name of the app.
        start : str or None
            Start code of the app.
        options : dict
            Options for the app.
        """
        self.name = name
        self.session_name = session_name
        self.class_name = class_name
        self.start = start
        self.options = options

    def __repr__(self):
        """
        Returns the string representation of a JaffleAppData.

        Returns
        -------
        repr : str
            String representation of a JaffleAppData.
        """
        return '<%s {name: %s session_name: %s class_name: %s start: %s}>' % (
            type(self).__name__, self.name, self.session_name, self.class_name, self.start)

    @classmethod
    def from_dict(cls, data):
        """
        Creates a JaffleAppData from a dict.

        Parameters
        ----------
        data : dict
            Python dict to initialize JaffleAppData.

        Returns
        -------
        app_data : JaffleAppData.
            App data.
        """
        return cls(**{a: data.get(a) for a in [
            'name', 'session_name', 'class_name', 'start', 'options'
        ]})

    def to_dict(self):
        """
        Returns the dict representation of a JaffleAppData.

        Returns
        -------
        app_data : dict
            Dict representation of a JaffleAppData.
        """
        return {
            'name': self.name,
            'session_name': self.session_name,
            'class_name': self.class_name,
            'start': self.start,
            'options': self.options
        }
