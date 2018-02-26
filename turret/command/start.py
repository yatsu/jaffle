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
import json
from jupyter_client.kernelspec import KernelSpecManager
import logging
from notebook.services.kernels.kernelmanager import MappingKernelManager
from notebook.services.contents.manager import ContentsManager
import os
from pathlib import Path
import select
import signal
import sys
import threading
from tornado import gen, ioloop
from tornado.escape import to_unicode
from traitlets import default
from traitlets.config.application import catch_config_error
import zmq
from zmq.eventloop import zmqstream
from .base import TurretBaseCommand
from ..status import TurretStatus
from ..process import Process
from ..session import TurretSessionManager


class TurretStartCommand(TurretBaseCommand):
    """
    Starts turret server.
    """
    description = __doc__

    @default('log_format')
    def _log_format_default(self):
        return ('%(time_color)s%(asctime)s.%(msecs).03d%(time_color_end)s '
                '%(name_color)s%(name)14s%(name_color_end)s '
                '%(level_color)s %(levelname)1.1s %(level_color_end)s %(message)s')

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
            kernel_spec_manager=self.kernel_spec_manager,
            kernel_manager_class='turret.kernel_manager.TurretKernelManager'
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

        self.status = TurretStatus(conf=self.conf)
        self.clients = {}
        self.procs = {}

    def start(self):
        self.log.debug('Starting turret')

        self.io_loop = ioloop.IOLoop.current()
        self.io_loop.add_callback(self._start_sessions)
        self.io_loop.add_callback(self._start_processes)

        ctx = zmq.Context.instance()
        self.socket = ctx.socket(zmq.PULL)
        self.port = self.socket.bind_to_random_port('tcp://*', min_port=9000, max_port=9999)
        self.log.info('Turret port: %s', self.port)

        stream = zmqstream.ZMQStream(self.socket)
        stream.on_recv(self.on_recv_message)

        try:
            self.io_loop.start()
        except KeyboardInterrupt:
            self.log.info('Interrupted...')

    def on_recv_message(self, msg):
        data = json.loads(to_unicode(msg[0]))
        self.log.debug('Receive message: %s', data)
        if data['type'] == 'log':
            payload = data['payload']
            level = getattr(logging, payload['levelname'].upper())
            if payload['args_type'] == 'tuple':
                args = tuple(payload['args'])
            else:
                args = payload['args']
            record = logging.getLogRecordFactory()(**dict(payload, level=level, args=args))
            logging.getLogger(data['app_name']).handle(record)

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
        self.socket.close()

        for client in self.clients.values():
            client.stop_channels()

        for session in self.session_manager.list_sessions():
            self.log.info('Deleting session: %s %s', session['name'], session['id'])
            yield self.session_manager.delete_session(session['id'])

        for sess_data in self.status.sessions.values():
            conn_file = self.kernel_connection_file_path(sess_data.kernel.id)
            if conn_file.exists():
                conn_file.unlink()

        for proc in self.procs.values():
            proc.stop()

        self.status.destroy(self.status_file_path)

        self.io_loop.stop()

    @gen.coroutine
    def _start_sessions(self):
        for session_name, data in self.conf.get('kernel', {}).items():
            self.log.info('Starting kernel: %s', session_name)
            startup = str(Path(__file__).parent.parent / 'startup.py')
            session_model = yield self.session_manager.create_session(
                name=session_name,
                kernel_name=data.get('kernel_name'),
                env={'PYTHONSTARTUP': startup}
            )
            # self.status.add_session(**dict(session_model, name=session_name))
            self.status.add_session(session_model['id'], session_name, session_model['kernel'])

        for session in self.status.sessions.values():
            kernel_id = session.kernel.id
            apps = self._get_apps_for_kernel_instance(session.name)
            if len(apps) == 0:
                continue
            kernel = self.kernel_manager.get_kernel(kernel_id)
            client = self.clients[session.name] = kernel.client()
            client.start_channels()
            client.wait_for_ready()

            for app_name, app_data in apps.items():
                logger = logging.getLogger(app_name)
                logger.parent = self.log

                if 'class' in app_data:
                    mod, cls = app_data['class'].rsplit('.', 1)
                    code = ('from {mod} import {cls}; {app} = {cls}({app!r}, {conf}, {port}, '
                            '{status}, **{opts})'.format(
                                mod=mod, cls=cls, app=app_name, conf=self.conf, port=self.port,
                                status=self.status.to_dict(), opts=app_data.get('options', {})))
                    if 'start' in app_data:
                        code += '; {}'.format(app_data['start'])
                    client.execute(code, silent=True)

                msg = client.shell_channel.get_msg(block=True)
                if msg['content']['status'] != 'ok':
                    self.log.error('Initializing kernel {!r} with app {!r} failed'
                                   .format(session.name, app_name))
                    print('\n'.join(msg['content']['traceback']), file=sys.stderr)

                self.status.add_app(name=app_name, session_name=session.name)

        self.status.save(self.status_file_path)

    @gen.coroutine
    def _start_processes(self):
        for proc_name, proc_data in self.conf.get('process', {}).items():
            logger = logging.getLogger(proc_name)
            logger.parent = self.log
            proc = self.procs[proc_name] = Process(logger, proc_name, **proc_data)
            yield proc.start()

    def _get_apps_for_kernel_instance(self, kernel_instance_name):
        return {name: data for name, data in self.conf.get('app', {}).items()
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
        sys.stdout.write('Shutdown this turret (%s/[%s])? ' % (yes, no))
        sys.stdout.flush()
        r, w, x = select.select([sys.stdin], [], [], 5)
        if r:
            line = sys.stdin.readline()
            if line.lower().startswith(yes) and no not in line.lower():
                self.log.critical('Shutdown confirmed')
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
