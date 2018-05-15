# -*- coding: utf-8 -*-

import json
import os
import re


VAR_PATTERN = re.compile(r'^J_VAR_[A-Za-z0-9_]+')
VAR_PREFIX = 'J_VAR_'


class NotFound(object):

    def __repr__(self):
        return 'NOT_FOUND'


class VariablesNamespace(object):
    """
    Variables namespace for loading jaffle.hcl.
    """

    _NOT_FOUND = NotFound()

    _TYPES = [str, bool, int, float, list, dict]

    def __init__(self, var_defs=None, vars=None, keep_undefined_vars=False):
        """
        Initializes VariablesNamespace.

        Parameters
        ----------
        var_defs : dict or None
            Variable definitions in format ``{ type: '...', default: ... }``.
        vars : dict
            Given variables.
        keep_undefined_vars : bool
            Whether to keep undefined variables as they are such as
            ``${var.foo}``. This option is required by loading variables
            (the first jaffle.hcl loading).
        """
        self.var_defs = var_defs
        self._variables = {
            name: self._get_hcl_value(
                name, var_def, (vars or {}).get(name, self._NOT_FOUND))
            for name, var_def in (var_defs or {}).items()
        }
        self._keep_undefined_vars = keep_undefined_vars

    def __repr__(self):
        """
        Returns string representation of VariablesNamespace.

        Returns
        -------
        repr : str
            String representation of VariablesNamespace.
        """
        return '<%s {variables: %s}>' % (type(self).__name__, self._variables)

    def _get_hcl_value(self, name, var_def, env_var):
        """
        Returns HCL value representation of the given variable.

        Parameters
        ----------
        name : str
            Variable name which is used only in an error message.
        var_def : dict
            Variable definition.
        env_var : object or _NOT_FOUND
            The value of the variable.
            If the variable was not passed by an environment variable,
            it is _NOT_FOUND

        Returns
        -------
        value : str
            HCL value representation of the given variable.

        Raises
        ------
        ValueError
            When the value cannot be converted to an HCL value.
        """
        default = var_def.get('default', self._NOT_FOUND)
        if env_var is self._NOT_FOUND:
            value = default
        else:
            value = env_var

        var_type = self._get_python_type(name, var_def.get('type', self._NOT_FOUND), default)

        try:
            if isinstance(value, str):
                if var_type is bool:
                    if value in ['true', '1']:
                        return 'true'
                    elif value in ['false', '0']:
                        return 'false'
                    raise ValueError('{!r} is not bool value'.format(value))
                elif var_type in [list, dict]:
                    obj = json.loads(value)
                    if not isinstance(obj, var_type):
                        raise ValueError('{!r} is not {}'.format(value, var_type))
                    return json.dumps(json.dumps(obj))
                elif var_type is str:
                    return value
                else:
                    return str(var_type(value))
            elif value in [self._NOT_FOUND, None]:
                return 'null'
            elif value is True:
                return 'true'
            elif value is False:
                return 'false'
            else:
                return json.dumps(value)

        except Exception as e:
            raise ValueError('Cannot convert {!r} to {} ({})'
                             .format(value, var_type.__name__, e))

    def _get_python_type(self, name, type_str, default):
        """
        Returns Python type of the given variable.
        If ``type_str`` is ``None``, the type will be infered based on the
        default value. If both ``type_str`` and ``default`` is ``None``,
        the type is going to be ``str``.

        Parameters
        ----------
        name : str
            Variable name which is used only in an error message.
        type_str : str or None
            Type name defined in jaffle.hcl. It may be ``_NOT_FOUND``.
        default : object
            Default value defined in jaffle.hcl. It may be ``_NOT_FOUND``.

        Returns
        -------
        type : type
            Python type of the given variable.

        Raises
        ------
        ValueError
            When the specified type is invalid.
            When the type of the default value is invalid.
        """
        for type_ in self._TYPES:
            if type_str == type_.__name__:
                return type_

        if type_str is self._NOT_FOUND:
            if default is self._NOT_FOUND:
                return str  # the default type is ``str``
            for type_ in self._TYPES:
                # infer the type based on the default value
                if isinstance(default, type_):
                    return type_
            raise ValueError('Invalid default value for {!r}: {!r}'.format(name, default))

        raise ValueError('Invalid type for {!r}: {!r}'.format(name, type_str))

    def __getattr__(self, name):
        """
        Returns the variable value. This method is called by the variables
        syntax in jaffle.hcl such as ``${var.foo}``.
        If ``self._keep_undefined_vars`` is true and the variable is not
        defined, the interpolation syntax returns as it is such as
        ``${var.foo}``.

        Parameters
        ----------
        name : str
            Variable name.

        Returns
        -------
        value : object
            Variable value.

        Raises
        ------
        KeyError
            When the specified variable is not found.
        """
        if self._keep_undefined_vars:
            return self._variables.get(name, '${var.%s}' % name)
        else:
            return self._variables[name]

    def __call__(self, name, default=None):
        """
        Returns the variable value. If the variable is not defined, returns
        the default value. This method is called by the variable syntax in
        jaffle.hcl such as ``${var('foo', '1')}``.

        Parameters
        ----------
        name : str
            Variable name.

        Returns
        -------
        value : object
            Variable value.
        """
        return self._variables.get(name, default)


def get_runtime_variables(command_line_variables):
    runtime_variables = {
        k[len(VAR_PREFIX):]: v for k, v in os.environ.items()
        if VAR_PATTERN.search(k)
    }
    runtime_variables.update(
        dict(tuple(v.split('=', 1)) for v in command_line_variables).items()
    )
    return runtime_variables
