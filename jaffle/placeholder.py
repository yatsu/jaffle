# -*- coding: utf-8 -*-

from itertools import chain


class FunctionPlaceholder(object):
    """
    A function placeholder for a template, which is used to keep an embedded
    function call as it is. (e.g. ``${func(1, 'a')}`` => ``${func(1,'a')}``)
    """

    def __init__(self, name):
        """
        Initializes FunctionPlaceholder.

        Parameters
        ----------
        name : str
            Function name.
        """
        self.name = name

    def __repr__(self):
        """
        Returns string representation of FunctionPlaceholder.

        Returns
        -------
        repr : str
            String representation of FunctionPlaceholder.
        """
        return '<%s {name: %s}>' % (type(self).__name__, self.name)

    def __call__(self, *args, **kwargs):
        """
        Renders the function call.

        Parameters
        ----------
        args : list[object]
            Positional arguments.
        kwargs : dict{str: object}
            Keyword arguments.

        Returns
        -------
        func_call : str
            Rendered function call.
        """
        return '${' + '{}({})'.format(
            self.name,
            ', '.join(chain(self._args(args), self._kwargs(kwargs)))
        ) + '}'

    def _args(self, args):
        """
        Renders positional arguments.

        Parameters
        ----------
        args : list[object]
            Positional arguments.

        rendered : list[str]
            Rendered positional arguments.
        """
        return (repr(a) for a in args)

    def _kwargs(self, kwargs):
        """
        Renders keyword arguments.

        Parameters
        ----------
        args : dict{str: object}
            Keyword arguments.

        rendered : list[str]
            Rendered keyword arguments.
        """
        return ('{}={!r}'.format(k, v) for k, v in kwargs.items())
