# -*- coding: utf-8 -*-

from tornado import web
from tornado.httputil import HTTPServerRequest
from unittest.mock import Mock, patch
from ..serverext import MyExtensionHandler


def test_myext_handler():
    app = Mock(web.Application, ui_methods={}, ui_modules={}, settings=dict(base_url='/'))
    req = Mock(HTTPServerRequest, connection=Mock())
    handler = MyExtensionHandler(app, req)

    with patch.object(handler, 'write') as write:
        handler.get()

    write.assert_called_once_with({'hello': 'world'})
