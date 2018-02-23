# -*- coding: utf-8 -*-

import json
import filelock
from pathlib import Path


class TurretStatus(object):

    def __init__(self, sessions={}, apps={}, lock_timeout=5):
        self.sessions = {}
        self.apps = {}
        self.lock_timeout = lock_timeout

    @classmethod
    def from_dict(cls, data):
        return cls(
            sessions={n: TurretSession.from_dict(s)
                      for n, s in data.get('sessions', {}).items()},
            apps={n: TurretAppData.from_dict(a)
                  for n, a in data.get('apps', {}).items()}
        )

    def add_session(self, id, name, kernel=None):
        session = TurretSession(id, name, kernel)
        self.sessions[session.name] = session

    def add_app(self, name, session_name):
        app = TurretAppData(name, session_name)
        self.apps[app.name] = app

    def to_dict(self):
        return {
            'sessions': {n: s.to_dict() for n, s in self.sessions.items()},
            'apps': {n: a.to_dict() for n, a in self.apps.items()}
        }

    @classmethod
    def load(cls, file_path, *args, **kwargs):
        status = cls(*args, **kwargs)

        with filelock.FileLock(str(file_path) + '.lock').acquire(timeout=status.lock_timeout):
            with Path(file_path).open() as f:
                data = json.load(f)

            for sess_name, sess_data in data.get('sessions', []).items():
                status.sessions[sess_name] = TurretSession(**sess_data)

            for app_name, app_data in data.get('apps', []).items():
                status.apps[app_name] = TurretAppData(**app_data)

        return status

    def save(self, file_path):
        with filelock.FileLock(str(file_path) + '.lock').acquire(timeout=self.lock_timeout):
            with file_path.open('w') as f:
                json.dump(self.to_dict(), f, indent=2)

    def destroy(self, file_path):
        if file_path.exists():
            with filelock.FileLock(str(file_path) + '.lock').acquire(timeout=self.lock_timeout):
                file_path.unlink()
        Path(str(file_path) + '.lock').unlink()


class TurretSession(object):

    def __init__(self, id, name, kernel=None):
        self.id = id
        self.name = name
        if kernel:
            self.kernel = TurretKernelData.from_dict(kernel)

    @classmethod
    def from_dict(cls, data):
        return cls(id=data.get('id'), name=data.get('name'), kernel=data.get('kernel'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'kernel': self.kernel.to_dict()
        }


class TurretKernelData(object):

    def __init__(self, id, name):
        self.id = id
        self.name = name

    @classmethod
    def from_dict(cls, data):
        return cls(**{a: data.get(a) for a in ['id', 'name']})

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class TurretAppData(object):

    def __init__(self, name, session_name=None):
        self.name = name
        self.session_name = session_name

    @classmethod
    def from_dict(cls, data):
        return cls(**{a: data.get(a) for a in ['name', 'session_name']})

    def to_dict(self):
        return {
            'name': self.name,
            'session_name': self.session_name
        }
