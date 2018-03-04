# -*- coding: utf-8 -*-

from prompt_toolkit.layout.lexers import Lexer
from pygments.token import Token


class PyTestLexer(Lexer):

    def lex_document(self, cli, document):
        lines = document.lines

        def get_line(lineno):
            try:
                line = lines[lineno]
                if '::' in line:
                    path, func = line.rsplit('::', 1)
                    return self._mod_tokens(path) + self._func_tokens(func)
                else:
                    return self._mod_tokens(line)

            except IndexError:
                return []

        return get_line

    def _mod_tokens(self, path):
        return [n for m in path.split('/')
                for n in [(Token.Name.Namespace, m), (Token.Name.Other, '/')]][:-1]

    def _func_tokens(self, func):
        return [(Token.Name.Other, '::'), (Token.Name.Function, func)]
