# -*- coding: utf-8 -*-

from tornado import web
from tornado.httputil import HTTPServerRequest
from unittest.mock import Mock
from ..webapp import APIHandler


def test_api_handler():
    app = Mock(web.Application, ui_methods={}, ui_modules={})
    req = Mock(HTTPServerRequest, connection=Mock())
    log = Mock()
    handler = APIHandler(app, req, log=log)
    assert handler.log is log
