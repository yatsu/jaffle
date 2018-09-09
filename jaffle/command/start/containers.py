# -*- coding: utf-8 -*-

from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.processors import Processor, Transformation
from prompt_toolkit.layout.screen import Char
from prompt_toolkit.layout.utils import explode_tokens
from prompt_toolkit.token import Token


class InputProcessor(Processor):

    def apply_transformation(self, cli, document, lineno, source_to_display, tokens):
        tokens = explode_tokens(tokens)
        return Transformation(tokens)


class InputWindow(Window):

    def __init__(self):
        super().__init__(
            content=BufferControl(
                buffer_name=DEFAULT_BUFFER,
                default_char=Char(token=Token),
                input_processors=[InputProcessor()]
            ),
            dont_extend_height=True
        )
