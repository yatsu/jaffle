# -*- coding: utf-8 -*-

from collections import Iterable
from functools import wraps
from mako.template import Template
from ..functions import functions


def _match_expand(func, match=None):
    """
    Wraps a function to call it with expanding matched patterns
    (e.g. ``\\1``, ``\\g<1>``, etc.).
    """
    if match is None:
        return func

    def expand(value):
        if isinstance(value, str):
            return match.expand(value)
        elif isinstance(value, dict):
            return {k: expand(v) for k, v in value.items()}
        elif isinstance(value, Iterable):
            return type(value)([expand(v) for v in value])
        else:
            return value

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*(expand(a) for a in args),
                    **{k: expand(v) for k, v in kwargs.items()})

    return wrapper


class TemplateString(str):
    """
    A string which may contain interpolation such as ``${var.hello}``, which
    can be ``render()``ed later.
    """

    def __new__(cls, string, namespace):
        """
        Constructs a TemplateString.
        This method is required to inherit ``str`` because ``str`` accepts
        only one argument.

        Parameters
        ----------
        string : str
            The contents of TemplateString.
        namespace : dict
            Namespace to be used to render.

        Returns
        -------
        tstr : TemplateString
            Constructed TemplateString.
        """
        return super().__new__(cls, string)

    def __init__(self, string, namespace):
        """
        Initializes TemplateString.

        Parameters
        ----------
        string : str
            The contents of TemplateString.
        namespace : dict
            Namespace to be used to render.
        """
        self.namespace = namespace

    def render(self, match=None):
        """
        Renders the string with processing interpolation and matched pattern
        expansion.

        Parameters
        ----------
        match : re.Match or None
            Matched pattern.

        Returns
        -------
        rendered : str
            Rendered string.
        """
        if match is not None:
            namespace = dict(
                self.namespace,
                **{f.__name__: _match_expand(f, match=match) for f in functions}
            )
        else:
            namespace = self.namespace
        return Template(self).render(**namespace)
