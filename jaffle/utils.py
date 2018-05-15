# -*- coding: utf-8 -*-

from copy import deepcopy
from functools import reduce


def deep_merge(*dicts, update=False):
    """
    Merges dicts deeply.

    Parameters
    ----------
    dicts : list[dict]
        List of dicts.
    update : bool
        Whether to update the first dict or create a new dict.

    Returns
    -------
    merged : dict
        Merged dict.
    """
    def merge_into(d1, d2):
        for key in d2:
            if key not in d1 or not isinstance(d1[key], dict):
                d1[key] = deepcopy(d2[key])
            else:
                d1[key] = merge_into(d1[key], d2[key])
        return d1

    if update:
        return reduce(merge_into, dicts[1:], dicts[0])
    else:
        return reduce(merge_into, dicts, {})


def bool_value(value):
    """
    Converts the given object to a bool if it is possible.

    Parameters
    ----------
    value : object
        Object to be converted to bool.

    Returns
    -------
    value : bool
        Bool value.

    Raises
    ------
    ValueError
        If the object cannot be converted to bool.
    """
    if isinstance(value, bool):
        return value

    if hasattr(value, 'render'):
        value = value.render()

    if value in ['true', '1']:
        return True
    elif value in ['false', '0']:
        return False

    raise ValueError('Invalid bool value: {!r}'.format(value))


def str_value(value, match=None):
    """
    Converts the given object to a string with processing interpolation and
    matched pattern expansion (``\\1``, ``\\g<1>``, etc.)>

    Parameters
    ----------
    match : re.Match or None
        Matched pattern.

    Returns
    -------
    value : str
        String value.
    """
    if hasattr(value, 'render'):
        return value.render(match=match)
    return str(value)
