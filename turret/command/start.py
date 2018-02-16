# -*- coding: utf-8 -*-

# Some part of this module was derived from Jupyter Notebook.
# https://github.com/jupyter/notebook/blob/master/notebook/notebookapp.py
#
# Jupyter Notebook license is as follows:
#
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from notebook.transutils import _  # noqa: required to import notebook classes
import hcl
from jupyter_client.kernelspec import KernelSpecManager
from notebook.services.kernels.kernelmanager import MappingKernelManager
from notebook.services.contents.manager import ContentsManager
import os
from pathlib import Path
import select
import signal
import sys
import threading
from tornado import gen, ioloop
from traitlets.config.application import catch_config_error
from .base import TurretBaseCommand
from ..session import TurretSessionManager


class TurretStartCommand(TurretBaseCommand):
    """
    Starts turret server.
    """
    description = __doc__

    def parse_command_line(self, argv):
        super().parse_command_line(argv)

        if self.extra_args:
            self.conf_file = Path(self.extra_args[0])
        else:
            self.conf_file = Path('turret.hcl')

    @catch_config_error
    def initialize(self, argv=None):
        super().initialize(argv)

        self.init_dir()

        self.kernel_spec_manager = KernelSpecManager(
            parent=self
        )
        self.kernel_manager = MappingKernelManager(
            parent=self,
            log=self.log,
            connection_dir=self.runtime_dir,
            kernel_spec_manager=self.kernel_spec_manager
        )
        self.contents_manager = ContentsManager(
            parent=self,
            log=self.log
        )
        self.session_manager = TurretSessionManager(
            parent=self,
            log=self.log,
            kernel_manager=self.kernel_manager,
            contents_manager=self.contents_manager
        )

        self.init_signal()

        self.load_conf()

        self.sessions = {}

    def start(self):
        self.log.debug('Starting turret')

        self.io_loop = ioloop.IOLoop.current()
        self.io_loop.add_callback(self._start_sessions)

        try:
            self.io_loop.start()
        except KeyboardInterrupt:
            self.log.info('Interrupted...')

    def init_signal(self):
        if not sys.platform.startswith('win') and sys.stdin and sys.stdin.isatty():
            signal.signal(signal.SIGINT, self._handle_sigint)
        signal.signal(signal.SIGTERM, self._signal_stop)

    def init_dir(self):
        self.log.debug('data_dir: %s', self.data_dir)
        self.log.debug('runtime_dir: %s', self.runtime_dir)
        os.environ['JUPYTER_DATA_DIR'] = self.data_dir

        data_dir = Path(self.data_dir)
        if not data_dir.exists():
            data_dir.mkdir()

        runtime_dir = Path(self.runtime_dir)
        if not runtime_dir.exists():
            runtime_dir.mkdir()

    def load_conf(self):
        with self.conf_file.open() as f:
            self.conf = hcl.load(f)
        self.log.debug('conf: %s', self.conf)

    @gen.coroutine
    def shutdown(self):
        for session in self.session_manager.list_sessions():
            self.log.info('Deleting session: %s %s', session['name'], session['id'])
            yield self.session_manager.delete_session(session['id'])

        for kernel_data in self.sessions.values():
            conn_file = self.kernel_connection_file(kernel_data['kernel']['id'])
            if conn_file.exists():
                conn_file.unlink()

        if self.sessions_file.exists():
            self.sessions_file.unlink()
        if self.sessions_lock_file.exists():
            self.sessions_lock_file.unlink()

        self.io_loop.stop()

    @gen.coroutine
    def _start_sessions(self):
        for kernel_instance_name, data in self.conf.get('kernel', {}).items():
            self.log.info('Starting kernel: %s', kernel_instance_name)
            startup = str(Path(__file__).parent.parent / 'startup.py')
            session_model = yield self.session_manager.create_session(
                name=kernel_instance_name,
                kernel_name=data.get('kernel_name'),
                env={'PYTHONSTARTUP': startup}
            )
            self.sessions[kernel_instance_name] = session_model

        for kernel_instance_name, session_model in self.sessions.items():
            kernel_id = session_model['kernel']['id']
            apps = self._get_apps_for_kernel_instance(kernel_instance_name)
            if len(apps) == 0:
                continue
            kernel = self.kernel_manager.get_kernel(kernel_id)
            client = kernel.client()
            client.start_channels()
            client.wait_for_ready()
            for app_name, app_data in apps.items():
                if 'class' in app_data:
                    mod, cls = app_data['class'].rsplit('.', 1)
                    client.execute(
                        'from {mod} import {cls}; {app} = {cls}({app!r}, {conf}, {sessions}, '
                        '**{opts})'.format(mod=mod, cls=cls, app=app_name, conf=self.conf,
                                           sessions=self.sessions,
                                           opts=app_data.get('options', {}))
                    )
                msg = client.shell_channel.get_msg(block=True)
                if msg['content']['status'] != 'ok':
                    client.stop_channels()
                    self.kernel_manager.shutdown_kernel(kernel_id)
                    self.log.error('Initializing kernel failed')
            client.stop_channels()

        self.write_sessions_file(self.sessions)

    def _get_apps_for_kernel_instance(self, kernel_instance_name):
        return {name: data for name, data in self.conf['app'].items()
                if data.get('kernel') == kernel_instance_name}

    def _handle_sigint(self, sig, frame):
        """
        SIGINT handler spawns confirmation dialog
        """
        # register more forceful signal handler for ^C^C case
        signal.signal(signal.SIGINT, self._signal_stop)
        # request confirmation dialog in bg thread, to avoid
        # blocking the App
        thread = threading.Thread(target=self._confirm_exit)
        thread.daemon = True
        thread.start()

    def _signal_stop(self, sig, frame):
        self.log.critical('Received signal %s, stopping', sig)
        self.io_loop.add_callback_from_signal(self.io_loop.stop)

    def _restore_sigint_handler(self):
        """
        callback for restoring original SIGINT handler
        """
        signal.signal(signal.SIGINT, self._handle_sigint)

    def _confirm_exit(self):
        """
        confirm shutdown on ^C

        A second ^C, or answering 'y' within 5s will cause shutdown,
        otherwise original SIGINT handler will be restored.

        This doesn't work on Windows.
        """
        self.log.info('Interrupted')
        yes = 'y'
        no = 'n'
        sys.stdout.write('Shutdown this notebook server (%s/[%s])? ' % (yes, no))
        sys.stdout.flush()
        r, w, x = select.select([sys.stdin], [], [], 5)
        if r:
            line = sys.stdin.readline()
            if line.lower().startswith(yes) and no not in line.lower():
                self.log.critical('Shutdown confirmed')

                if self.sessions_file.exists():
                    self.sessions_file.unlink()

                # schedule stop on the main thread,
                # since this might be called from a signal handler
                self.io_loop.add_callback_from_signal(self.shutdown)

                return
        else:
            print('No answer for 5s:', end=' ')
        print('resuming operation...')
        # no answer, or answer is no:
        # set it back to original SIGINT handler
        # use IOLoop.add_callback because signal.signal must be called
        # from main thread
        self.io_loop.add_callback_from_signal(self._restore_sigint_handler)
