# -*- coding: utf-8 -*-

from collections import namedtuple
from prompt_toolkit.cache import SimpleCache
from prompt_toolkit.layout.controls import UIControl, UIContent
from prompt_toolkit.layout.lexers import SimpleLexer
from prompt_toolkit.layout.screen import Char, Point
from pygments.token import Token


_ProcessedLine = namedtuple('_ProcessedLine', 'tokens source_to_display display_to_source')


class LogControl(UIControl):

    def __init__(self, document):
        self.document = document
        self.lexer = SimpleLexer()
        self.input_processors = []
        self.default_char = Char(token=Token.Transparent)

        self._token_cache = SimpleCache(maxsize=8)

    def reset(self):
        pass

    def preferred_width(self, cli, max_available_width):
        return None

    def preferred_height(self, cli, width, max_available_height, wrap_lines):
        # Calculate the content height, if it was drawn on a screen with the given width.
        height = 0
        content = self.create_content(cli, width, None)

        # When line wrapping is off, the height should be equal to the amount of lines.
        if not wrap_lines:
            return content.line_count

        # When the number of lines exceeds the max_available_height, just return
        # max_available_height. No need to calculate anything.
        if content.line_count >= max_available_height:
            return max_available_height

        for i in range(content.line_count):
            height += content.get_height_for_line(i, width)

            if height >= max_available_height:
                return max_available_height

        return height

    def has_focus(self, cli):
        """
        Whether the control has the focus.
        """
        return False

    def create_content(self, cli, width, height):
        """
        Generate the content for this user control.

        Returns a :class:`.UIContent` instance.
        """
        get_processed_line = self._create_get_processed_line_func(cli, self.document)
        self._last_get_processed_line = get_processed_line

        def translate_rowcol(row, col):
            " Return the content column for this coordinate. "
            return Point(y=row, x=get_processed_line(row).source_to_display(col))

        def get_line(i):
            " Return the tokens for a given line number. "
            tokens = get_processed_line(i).tokens

            # Add a space at the end, because that is a possible cursor
            # position. (When inserting after the input.) We should do this on
            # all the lines, not just the line containing the cursor. (Because
            # otherwise, line wrapping/scrolling could change when moving the
            # cursor around.)
            tokens = tokens + [(self.default_char.token, ' ')]
            return tokens

        return UIContent(
            get_line=get_line,
            line_count=self.document.line_count,
            cursor_position=translate_rowcol(self.document.cursor_position_row,
                                             self.document.cursor_position_col),
            default_char=self.default_char
        )

    def mouse_handler(self, cli, mouse_event):
        """
        Handle mouse events.

        When `NotImplemented` is returned, it means that the given event is not
        handled by the `UIControl` itself. The `Window` or key bindings can
        decide to handle this event as scrolling or changing focus.

        :param cli: `CommandLineInterface` instance.
        :param mouse_event: `MouseEvent` instance.
        """
        return NotImplemented

    def move_cursor_down(self, cli):
        """
        Request to move the cursor down.
        This happens when scrolling down and the cursor is completely at the
        top.
        """
        pass

    def move_cursor_up(self, cli):
        """
        Request to move the cursor up.
        """
        pass

    def _get_tokens_for_line_func(self, cli, document):
        """
        Create a function that returns the tokens for a given line.
        """
        # Cache using `document.text`.
        def get_tokens_for_line():
            return self.lexer.lex_document(cli, document)

        return self._token_cache.get(document.text, get_tokens_for_line)

    def _create_get_processed_line_func(self, cli, document):
        """
        Create a function that takes a line number of the current document and
        returns a _ProcessedLine(processed_tokens, source_to_display, display_to_source)
        tuple.
        """
        def transform(lineno, tokens):
            " Transform the tokens for a given line number. "
            source_to_display_functions = []
            display_to_source_functions = []

            # Get cursor position at this line.
            if document.cursor_position_row == lineno:
                cursor_column = document.cursor_position_col
            else:
                cursor_column = None

            def source_to_display(i):
                """ Translate x position from the buffer to the x position in the
                processed token list. """
                for f in source_to_display_functions:
                    i = f(i)
                return i

            # Apply each processor.
            for p in self.input_processors:
                transformation = p.apply_transformation(
                    cli, document, lineno, source_to_display, tokens)
                tokens = transformation.tokens

                if cursor_column:
                    cursor_column = transformation.source_to_display(cursor_column)

                display_to_source_functions.append(transformation.display_to_source)
                source_to_display_functions.append(transformation.source_to_display)

            def display_to_source(i):
                for f in reversed(display_to_source_functions):
                    i = f(i)
                return i

            return _ProcessedLine(tokens, source_to_display, display_to_source)

        def create_func():
            get_line = self._get_tokens_for_line_func(cli, document)
            cache = {}

            def get_processed_line(i):
                try:
                    return cache[i]
                except KeyError:
                    processed_line = transform(i, get_line(i))
                    cache[i] = processed_line
                    return processed_line
            return get_processed_line

        return create_func()
