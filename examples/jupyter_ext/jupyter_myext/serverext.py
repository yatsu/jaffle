# -*- coding: utf-8 -*-

from notebook.base.handlers import APIHandler, json_errors


class MyExtensionHandler(APIHandler):

    @json_errors
    def get(self):
        self.write({'hello': 'world'})
