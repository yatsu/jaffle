# -*- coding: utf-8 -*-

# Some part of this module was derived from Jupyter Notebook.
# https://github.com/jupyter/notebook/blob/master/notebook/notebookapp.py
#
# Jupyter Notebook license is as follows:
#
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

try:
    from notebook.transutils import _  # noqa: required to import notebook classes
except ImportError:
    pass
from functools import partial
import hcl
import json
from jupyter_client.kernelspec import KernelSpecManager
import logging
from mako.template import Template
from notebook.services.contents.manager import ContentsManager
from notebook.services.kernels.kernelmanager import MappingKernelManager
import os
from pathlib import Path
import re
import select
import signal
import sys
import threading
from tornado import gen, ioloop
from tornado.escape import to_unicode
from traitlets import default, Dict, Instance, Int, List, Unicode
from traitlets.config.application import catch_config_error
import zmq
from zmq.eventloop import zmqstream
from ...kernel_client import JaffleKernelClient
from ...process import Process
from ...session import JaffleSessionManager
from ...status import JaffleStatus
from ...utils import deep_merge
from ..base import BaseJaffleCommand
from ..functions import functions
from .variables import VariablesNamespace


class JaffleStartCommand(BaseJaffleCommand):
    """
    Starts jaffle server.
    """

    _ENV_PATTERN = re.compile(r'^[A-Za-z0-9_]+')
    _VAR_PATTERN = re.compile(r'^T_VAR_[A-Za-z0-9_]+')
    _VAR_PREFIX = 'T_VAR_'

    description = __doc__

    aliases = dict(BaseJaffleCommand.aliases,
                   variables='JaffleStartCommand.variables')

    @default('log_format')
    def _log_format_default(self):
        return ('%(time_color)s%(asctime)s.%(msecs).03d%(time_color_end)s '
                '%(name_color)s%(name)14s%(name_color_end)s '
                '%(level_color)s %(levelname)1.1s %(level_color_end)s %(message)s')

    conf_files = List(Instance(Path))
    variables = List(Unicode(), default_value=[], config=True)

    parsed_variables = Dict(default_value={})
    conf = Dict(default_value={})
    status = Instance(JaffleStatus, allow_none=True)
    clients = Dict(default_value={})
    procs = Dict(default_value={})
    jobs = Dict(default_value={})
    socket = Instance('zmq.Socket', allow_none=True)
    port = Int(allow_none=True)
    io_loop = Instance(ioloop.IOLoop, allow_none=True)

    kernel_spec_manager = Instance(KernelSpecManager, allow_none=True)
    kernel_manager = Instance(MappingKernelManager, allow_none=True)
    contents_manager = Instance(ContentsManager, allow_none=True)
    session_manager = Instance(JaffleSessionManager, allow_none=True)

    def parse_command_line(self, argv):
        """
        Parses comnand line.

        Parameters
        ----------
        argv : list[str]
            Command line strings.
        """
        super().parse_command_line(argv)

        for var in self.variables:
            if '=' not in var:
                print('Invalid variable assignment: {!r}'.format(var))
                sys.exit(1)

        if self.extra_args:
            self.conf_files = [Path(a) for a in self.extra_args]
        else:
            self.conf_files = [Path('jaffle.hcl')]

        for f in self.conf_files:
            if not f.exists():
                print('File not found: {!r}'.format(str(f)), file=sys.stderr)
                sys.exit(1)

    @catch_config_error
    def initialize(self, argv=None):
        """
        Initializes JaffleServer.
        Setup Jupyter and Jaffle managers before starting the server.

        Parameters
        ----------
        argv : list[str]
            Command line strings.
        """
        super().initialize(argv)

        self.check_running()

        self.init_dir()

        self.kernel_spec_manager = KernelSpecManager(
            parent=self
        )
        self.kernel_manager = MappingKernelManager(
            parent=self,
            log=self.log,
            connection_dir=self.runtime_dir,
            kernel_spec_manager=self.kernel_spec_manager,
            kernel_manager_class='jaffle.kernel_manager.JaffleKernelManager'
        )
        self.contents_manager = ContentsManager(
            parent=self,
            log=self.log
        )
        self.session_manager = JaffleSessionManager(
            parent=self,
            log=self.log,
            kernel_manager=self.kernel_manager,
            contents_manager=self.contents_manager
        )

        self.init_signal()

        self.load_conf()

        self.status = JaffleStatus(pid=os.getpid(), conf=self.conf)

    def check_running(self):
        """
        Checks whether Jaffle is already running.
        """
        if self.status_file_path.exists():
            print("Jaffle is already running in this directory.",
                  "Execute 'jaffle stop' to force stop the running Jaffle.",
                  file=sys.stderr)
            sys.exit(1)

    def init_dir(self):
        """
        Creates directories.
        """
        self.log.debug('runtime_dir: %s', self.runtime_dir)
        os.environ['JUPYTER_DATA_DIR'] = self.runtime_dir

        runtime_dir = Path(self.runtime_dir)
        if not runtime_dir.exists():
            runtime_dir.mkdir()

    def init_signal(self):
        """
        Initializes signal handlers.
        """
        if self.answer_yes:
            signal.signal(signal.SIGINT, self._signal_stop)
        else:
            signal.signal(signal.SIGINT, self._handle_sigint)
        signal.signal(signal.SIGTERM, self._signal_stop)

    def load_conf(self):
        """
        Loads config from ``jaffle.hcl``.
        """
        try:
            vars = {k[len(self._VAR_PREFIX):]: v for k, v in os.environ.items()
                    if self._VAR_PATTERN.search(k)}
            vars.update(dict(tuple(var.split('=', 1)) for var in self.variables).items())
            ns = {k: v for k, v in os.environ.items()
                  if self._ENV_PATTERN.search(k) and not self._VAR_PATTERN.search(k)}
            ns.update({f.__name__: f for f in functions})
            self.conf = deep_merge(*(self._load_conf_file(f, vars, ns)
                                     for f in self.conf_files))

        except ValueError as e:
            print('Configuration error: {}'.format(e), file=sys.stderr)
            sys.exit(1)

        self.app_log_suppress_patterns = {
            app_name: [re.compile(r) for r in app_data.get('logger', {}).get('suppress_regex', [])]
            for app_name, app_data in self.conf.get('app', {}).items()
        }
        self.app_log_replace_patterns = {
            app_name: [(re.compile(r['from']), r['to'])
                       for r in app_data.get('logger', {}).get('replace_regex', [])]
            for app_name, app_data in self.conf.get('app', {}).items()
        }
        self.global_log_suppress_patterns = [
            re.compile(r)
            for r in self.conf.get('logger', {}).get('suppress_regex', [])
        ]
        self.global_log_replace_patterns = [
            (re.compile(r['from']), r['to'])
            for r in self.conf.get('logger', {}).get('replace_regex', [])
        ]

    def start(self):
        """
        Starts Jaffle server and creates a ZeroMQ channel to receive messages
        from Jaffle app.
        """
        self.log.debug('Starting jaffle')

        try:
            self.io_loop = ioloop.IOLoop.current()
            self.io_loop.add_callback(self._start_sessions)
            self.io_loop.add_callback(self._start_processes)

            self._init_job_loggers()

            ctx = zmq.Context.instance()
            self.socket = ctx.socket(zmq.PULL)
            self.port = self.socket.bind_to_random_port('tcp://*', min_port=9000, max_port=9099)
            self.log.info('Jaffle port: %s', self.port)

            stream = zmqstream.ZMQStream(self.socket, self.io_loop)
            stream.on_recv(self._on_recv_msg)

            self.io_loop.start()

        except KeyboardInterrupt:
            self.log.info('Interrupted...')

        except Exception as e:
            if self.log_evel == logging.DEBUG:
                self.log.exception(e)
            else:
                self.log.error(e)
            sys.exit(1)

    @gen.coroutine
    def shutdown(self):
        """
        Shuts down Jaffle server

        Returns
        -------
        future : tornado.gen.Future
            Future of shutting down ``jaffle start``.
        """
        self.socket.close()

        for client in self.clients.values():
            client.stop_channels()

        for jupyter_sess in self.session_manager.list_sessions():
            self.log.info('Deleting jupyter_sess: %s %s',
                          jupyter_sess['name'], jupyter_sess['id'])
            yield self.session_manager.delete_session(jupyter_sess['id'])

        for jaffle_sess in self.status.sessions.values():
            conn_file = self.kernel_connection_file_path(jaffle_sess.kernel.id)
            if conn_file.exists():
                conn_file.unlink()

        for proc in self.procs.values():
            proc.stop()

        self.status.destroy(self.status_file_path)

        self.io_loop.stop()

    def _load_conf_file(self, conf_file_path, vars, namespace):
        """
        Loads config from a configuration file.

        Parameters
        ----------
        conf_file_path : pathlib.Path
            Configuration file path.
        vars : dict
            Environment variables.
        namespace : dict
            Namespace for the configuration template.
            It will be updated in this method.

        Returns
        -------
        conf : dict
            Jaffle configuration.
        """
        template = Template(filename=str(conf_file_path))

        # Use the dummy ``var`` to load variables
        old_var = namespace.get('var', VariablesNamespace({}))
        namespace['var'] = VariablesNamespace(keep_undefined_vars=True)
        first_rendered = template.render(**namespace)
        conf_for_vars = hcl.loads(first_rendered)

        # Convert "${var.foo}" to ${var.foo}
        template = Template(re.sub(r'"(\$\{.*\})"', r'\1', first_rendered))

        # Insert the real variables to ``var`` and load the config again
        namespace['var'] = VariablesNamespace(
            deep_merge(old_var.var_defs, conf_for_vars.get('variable', {})),
            vars=vars
        )
        self.log.debug('variables: %s', namespace['var'])
        return hcl.loads(template.render(**namespace))

    @gen.coroutine
    def _start_sessions(self):
        """
        Starts kernels and sessions, executes apps' code in it.

        Returns
        -------
        future : tornado.gen.Future
            Future of starting all sessions.
        """
        try:
            kernels = self.conf.get('kernel', {})
            for session_name, data in kernels.items():  # session_name == kernel instance name
                self.log.info('Starting kernel: %s', session_name)
                startup = str(Path(__file__).parent.parent.parent / 'startup.py')
                session_model = yield self.session_manager.create_session(
                    name=session_name,
                    kernel_name=data.get('kernel_name'),
                    env={'PYTHONSTARTUP': startup}
                )
                self.status.add_session(session_model['id'], session_name, session_model['kernel'])

            for session in self.status.sessions.values():
                kernel_id = session.kernel.id
                apps = self._get_apps_for_session(session.name)
                if len(apps) == 0:
                    continue

                kernel_manager = self.kernel_manager.get_kernel(kernel_id)
                kernel_manager.client_factory = JaffleKernelClient
                client = self.clients[session.name] = kernel_manager.client()
                client.start_channels()
                client.shell_channel.add_handler(partial(
                    self._handle_shell_msg, session, kernel_manager
                ))

                code_lines = []

                env = {e: os.getenv(e, '') for e in kernels[session.name].get('pass_env', [])}
                if len(env) > 0:
                    code_lines.append('import os')
                    code_lines.append('\n'.join(['os.environ[{!r}] = {!r}'.format(k, v)
                                                 for k, v in env.items()]))

                for app_name, app_data in apps.items():
                    if app_data.get('disabled', False):
                        continue
                    logger = logging.getLogger(app_name)
                    logger.parent = self.log
                    logger.setLevel(logging.DEBUG)
                    # app's log level in the jaffle server process is always DEBUG,
                    # whereas it varies in the kernel instance depending on the
                    # configuration

                    if 'class' in app_data:
                        mod, cls = app_data['class'].rsplit('.', 1)
                        opts = app_data.get('options', {})
                        self.log.info('Initializing %s.%s on %s', mod, cls, session.name)
                        self.log.debug('options for %s: %s', cls, opts)
                        code_lines.append('from {} import {}'.format(mod, cls))
                        code_lines.append(
                            '{app} = {cls}({app!r}, {conf}, {port}, {status}, **{opts})'
                            .format(cls=cls, app=app_name, conf=self.conf, port=self.port,
                                    status=self.status.to_dict(), opts=opts)
                        )
                        if 'start' in app_data:
                            code_lines.append(app_data['start'])

                    self.status.add_app(name=app_name, session_name=session.name)

                client.execute('\n'.join(code_lines), silent=True)

            self.status.save(self.status_file_path)

        except Exception as e:
            if self.log_level == logging.DEBUG:
                self.log.exception(e)
            else:
                self.log.error(e)
            sys.exit(1)

    def _on_recv_msg(self, msg):
        """
        Handles a ZeroMQ message from Jaffle apps.

        Parameters
        ----------
        msg : str
            JSON encoded message.
        """
        data = json.loads(to_unicode(msg[0]))
        self.log.debug('Receive message: %s', data)
        if data['type'] == 'log':
            app_name = data['app_name']
            payload = data['payload']
            logger_name = payload.get('logger') or app_name
            level = getattr(logging, payload['levelname'].upper())
            msg = payload.get('message', '')
            if not any([r.search(msg) for r in
                        self.app_log_suppress_patterns.get(app_name, []) +
                        self.global_log_suppress_patterns]):
                for pattern, replace in (
                        self.app_log_replace_patterns.get(app_name, []) +
                        self.global_log_replace_patterns):
                    msg = pattern.sub(replace, msg)
                logging.getLogger(logger_name).log(level, msg)

    @gen.coroutine
    def _start_processes(self):
        """
        Starts external processes.

        Returns
        -------
        future : tornado.gen.Future
            Future of starting all external processes.
        """
        processes = []
        for proc_name, proc_data in self.conf.get('process', {}).items():
            if proc_data.get('disabled', False):
                continue
            logger = logging.getLogger(proc_name)
            logger.parent = self.log
            logger_data = proc_data.get('logger', {})
            logger.setLevel(getattr(logging, logger_data.get('level', 'info').upper()))
            proc = self.procs[proc_name] = Process(
                logger, proc_name, proc_data.get('command'),
                proc_data.get('tty', False), proc_data.get('env', {}),
                logger_data.get('suppress_regex', []),
                logger_data.get('replace_regex', []),
                self.color
            )
            processes.append(proc.start())
        yield processes

    def _init_job_loggers(self):
        """
        Initializes job loggers.
        """
        for job_name, job_data in self.conf.get('job', {}).items():
            logger_data = job_data.get('logger', {})
            logger_name = logger_data.get('name', job_name)
            logger = logging.getLogger(logger_name)
            logger.parent = self.log
            logger.setLevel(getattr(logging, logger_data.get('level', 'info').upper()))

    def _get_apps_for_session(self, session_name):
        """
        Gets app data for the given session.

        Parameters
        ----------
        session_name : str
            Jaffle session name (= kernel instance name defined in jaffle.hcl).

        Returns
        -------
        apps : dict{str: dict}
            App data.
        """
        return {name: data for name, data in self.conf.get('app', {}).items()
                if data.get('kernel') == session_name}

    def _handle_sigint(self, sig, frame):
        """
        SIGINT handler spawns confirmation dialog

        Parameters
        ----------
        sig : int
            Signal number.
        frame: frame
            Interrupted stack frame.
        """
        # register more forceful signal handler for ^C^C case
        signal.signal(signal.SIGINT, self._signal_stop)
        # request confirmation dialog in bg thread, to avoid
        # blocking the App
        thread = threading.Thread(target=self._confirm_exit)
        thread.daemon = True
        thread.start()

    def _signal_stop(self, sig, frame):
        """
        SIGINT handler for force shutdown by double ``Ctrl-C``.

        Parameters
        ----------
        sig : int
            Signal number.
        frame: frame
            Interrupted stack frame.
        """
        self.log.critical('Received signal %s, stopping', sig)
        self.io_loop.add_callback_from_signal(self.shutdown)

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
        sys.stdout.write('Shutdown this jaffle (%s/[%s])? ' % (yes, no))
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

    def _handle_shell_msg(self, session, kernel_manager, msg):
        """
        Handles Shell channel message.

        Parameters
        ----------
        session : JaffleSession
            Jaffle session
        kernel_manager : JaffleKernelManager
            Kernel manager.
        msg : dict
            Shell message.
        """
        if kernel_manager.is_ready:
            return

        if msg['msg_type'] == 'execute_reply' and msg['content'].get('status') == 'ok':
            kernel_manager.is_ready = True
            self.log.info('Kernel %s (%s) is ready', session.name, session.kernel.id)
