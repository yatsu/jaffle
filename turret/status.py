# -*- coding: utf-8 -*-

import json
import filelock
from pathlib import Path


class TurretStatus(object):
    """
    Turret server status.
    """

    def __init__(self, sessions={}, apps={}, conf={}, lock_timeout=5):
        """
        Initializes TurretStatus.

        Parameters
        ----------
        sessions : dict{src: dict}
            Turret sessions.
        apps : dict
            Current running apps data.
        conf : dict
            Turret configuration.
        lock_timeout : int
            File lock timeout.
        """
        self.sessions = {}
        self.apps = {}
        self.conf = conf
        self.lock_timeout = lock_timeout

    def __repr__(self):
        """
        Returns the string representation of TurretStatus.

        Returns
        -------
        repr : str
            String representation of TurretStatus.
        """
        return '<%s {#sessions: %d #apps: %d}>' % (
            self.__class__.__name__, len(self.sessions), len(self.apps))

    @classmethod
    def from_dict(cls, data):
        """
        Creates a TurretStatus from a dict.

        Parameters
        ----------
        data : dict
            Python dict to initialize TurretStatus.

        Returns
        -------
        status : TurretStatus
            Turret server status.
        """
        return cls(
            sessions={n: TurretSession.from_dict(s)
                      for n, s in data.get('sessions', {}).items()},
            apps={n: TurretAppData.from_dict(a)
                  for n, a in data.get('apps', {}).items()},
            conf=data.get('conf'),
            lock_timeout=data.get('lock_timeout', 5)
        )

    def add_session(self, id, name, kernel=None):
        """
        Creates a Turret session and registers it to a TurretStatus.

        Parameters
        ----------
        id : str
            Session ID (UUID).
        name : str
            Turret session name.
        kernel : dict
            A dict of Kernel ID and name.
        """
        session = TurretSession(id, name, kernel)
        self.sessions[session.name] = session

    def add_app(self, name, session_name):
        """
        Creates a Turret app data and registers it to a TurretStatus.

        Parameters
        ----------
        name : str
            App name.
        session_name : str
            Turret session name (= kernel instance name defined in turret.hcl).
        """
        app = TurretAppData(name, session_name)
        self.apps[app.name] = app

    def to_dict(self):
        """
        Returns the dict representation of a TurretStatus.

        Returns
        -------
        status : dict
            Dict representation of a TurretStatus.
        """
        return {
            'sessions': {n: s.to_dict() for n, s in self.sessions.items()},
            'apps': {n: a.to_dict() for n, a in self.apps.items()},
            'conf': self.conf
        }

    @classmethod
    def load(cls, file_path):
        """
        Loads TurretStatus from a file.

        Parameters
        ----------
        file_path : pathlib.Path or str
            File path.

        Returns
        -------
        status : TurretStatus
            Turret server status.
        """
        status = cls()

        with filelock.FileLock(str(file_path) + '.lock').acquire(timeout=status.lock_timeout):
            with Path(file_path).open() as f:
                data = json.load(f)

            for sess_name, sess_data in data.get('sessions', []).items():
                status.sessions[sess_name] = TurretSession(**sess_data)

            for app_name, app_data in data.get('apps', []).items():
                status.apps[app_name] = TurretAppData(**app_data)

            status.conf = data['conf']

        return status

    def save(self, file_path):
        """
        Saves TurretStatus to a file.

        Parameters
        ----------
        file_path : pathlib.Path or str
            File path.
        """
        with filelock.FileLock(str(file_path) + '.lock').acquire(timeout=self.lock_timeout):
            with file_path.open('w') as f:
                json.dump(self.to_dict(), f, indent=2)

    def destroy(self, file_path):
        """
        Deletes the TurretStatus file and the lock file of it.

        Parameters
        ----------
        file_path : pathlib.Path or str
            File path.
        """
        if file_path.exists():
            with filelock.FileLock(str(file_path) + '.lock').acquire(timeout=self.lock_timeout):
                file_path.unlink()
        Path(str(file_path) + '.lock').unlink()


class TurretSession(object):
    """
    Turret session.
    """

    def __init__(self, id, name, kernel=None):
        """
        Initializes TurretSession.

        Parameters
        ----------
        id : str
            Session ID (UUID).
        name : str
            Turret session name (= kernel instance name defined in turret.hcl).
        kernel : dict or None
            A dict of Kernel ID and name.
        """
        self.id = id
        self.name = name
        if kernel:
            self.kernel = TurretKernelData.from_dict(kernel)

    def __repr__(self):
        """
        Returns the string representation of a TurretSession.

        Returns
        -------
        repr : str
            String representation of a TurretSession.
        """
        return '<%s {id: %s name: %s kernel: %s}>' % (
            self.__class__.__name__, self.id, self.name, self.kernel)

    @classmethod
    def from_dict(cls, data):
        """
        Creates a TurretSession from a dict.

        Parameters
        ----------
        data : dict
            Python dict to initialize TurretSession.

        Returns
        -------
        session : TurretSession.
            Turret session.
        """
        return cls(id=data.get('id'), name=data.get('name'), kernel=data.get('kernel'))

    def to_dict(self):
        """
        Returns the dict representation of a TurretSession.

        Returns
        -------
        session : dict
            Dict representation of a TurretSession.
        """
        return {
            'id': self.id,
            'name': self.name,
            'kernel': self.kernel.to_dict()
        }


class TurretKernelData(object):
    """
    Turret kernel data.
    """

    def __init__(self, id, name):
        """
        Initializes TurretKernelData.

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
        Returns the string representation of a TurretKernelData.

        Returns
        -------
        repr : str
            String representation of a TurretKernelData.
        """
        return '<%s {id: %s name: %s}>' % (
            self.__class__.__name__, self.id, self.name)

    @classmethod
    def from_dict(cls, data):
        """
        Creates a TurretKernelData from a dict.

        Parameters
        ----------
        data : dict
            Python dict to initialize TurretKernelData.

        Returns
        -------
        kernel_data : TurretKernelData.
            Kernel data.
        """
        return cls(**{a: data.get(a) for a in ['id', 'name']})

    def to_dict(self):
        """
        Returns the dict representation of a TurretKernelData.

        Returns
        -------
        kernel_data : dict
            Dict representation of a TurretKernelData.
        """
        return {
            'id': self.id,
            'name': self.name
        }


class TurretAppData(object):
    """
    Turret app data.
    """

    def __init__(self, name, session_name=None):
        """
        Initializes TurretAppData.

        Parameters
        ----------
        name : str
            App name.
        session_name : str
            Turret session name (= kernel instance name defined in turret.hcl).
        """
        self.name = name
        self.session_name = session_name

    def __repr__(self):
        """
        Returns the string representation of a TurretAppData.

        Returns
        -------
        repr : str
            String representation of a TurretAppData.
        """
        return '<%s {name: %s session_name: %s}>' % (
            self.__class__.__name__, self.name, self.session_name)

    @classmethod
    def from_dict(cls, data):
        """
        Creates a TurretAppData from a dict.

        Parameters
        ----------
        data : dict
            Python dict to initialize TurretAppData.

        Returns
        -------
        app_data : TurretAppData.
            App data.
        """
        return cls(**{a: data.get(a) for a in ['name', 'session_name']})

    def to_dict(self):
        """
        Returns the dict representation of a TurretAppData.

        Returns
        -------
        app_data : dict
            Dict representation of a TurretAppData.
        """
        return {
            'name': self.name,
            'session_name': self.session_name
        }
