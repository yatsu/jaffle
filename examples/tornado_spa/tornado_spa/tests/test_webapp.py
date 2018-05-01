# -*- coding: utf-8 -*-

from tornado import web
from tornado.httputil import HTTPServerRequest
from unittest.mock import Mock
from ..webapp import APIExampleHandler, ExampleWebApp


def test_api_handler():
    app = Mock(web.Application, ui_methods={}, ui_modules={})
    req = Mock(HTTPServerRequest, connection=Mock())
    log = Mock()
    handler = APIExampleHandler(app, req, log=log)
    assert handler.log is log


def test_example_web_app():
    app = ExampleWebApp(Mock())
    assert isinstance(app, ExampleWebApp)
