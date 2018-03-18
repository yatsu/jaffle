# -*- coding: utf-8 -*-

from notebook.utils import url_path_join
from .serverext import MyExtensionHandler


def load_jupyter_server_extension(nb_server_app):
    nb_server_app.log.info('Loading jupyter_myext...')

    web_app = nb_server_app.web_app
    url_myext = url_path_join(web_app.settings['base_url'], '/api/myext')
    web_app.add_handlers(r'.*$', [(url_myext, MyExtensionHandler)])


def _jupyter_server_extension_paths():
    return [{'module': 'jupyter_myext'}]


def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'jupyter_myext',
        'require': 'jupyter_myext/notebook'
    }]
