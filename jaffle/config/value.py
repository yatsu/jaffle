# -*- coding: utf-8 -*-

from .template_string import TemplateString


class _NO_DEFAULT(object):
    pass


class ConfigValue(object):
    """
    Configuration value's base class.
    """

    def __init__(self, namespace=None):
        """
        Initializes ConfigValue.

        Parameters
        ----------
        namespace : dict
            Namespace for string interpolation.
        """
        self.namespace = namespace or {}
        self.value = None

    def __repr__(self):
        """
        Returns the string representation of ConfigValue.

        Returns
        -------
        repr : str
            String representation of ConfigValue.
        """
        return repr(self.value)

    def __eq__(self, other):
        """
        Checks if two values are equal.

        Parameters
        ----------
        other : object
            Another value.
        """
        return (isinstance(other, ConfigValue) and
                other.value == self.value and other.namespace == self.namespace)

    @classmethod
    def create(self, value, namespace=None):
        """
        Create a concrete config value depending on type of the provided value.

        Parameters
        ----------
        value : object
            Value object.
        namespace : dict
            Namespace for string interpolation.

        Returns
        -------
        value : ConfigDict, ConfigList or object
            Concrete config value.
        """
        if isinstance(value, list):
            return ConfigList(value, namespace=namespace)
        elif isinstance(value, dict):
            return ConfigDict(value, namespace=namespace)
        else:
            return value


class ConfigCollection(ConfigValue):
    """
    Configuration value as a collection.
    """

    def __repr__(self):
        """
        Returns the string representation of ConfigCollection.

        Returns
        -------
        repr : str
            String representation of ConfigCollection.
        """
        return repr(self.raw())

    def __iter__(self):
        """
        Iterates over the collection.

        Returns
        -------
        iter : iterator
            Iterator to the collection.
        """
        return iter(self.value)

    def __len__(self):
        """
        Returns the length of the collection.

        Returns
        -------
        len : int
            Length of the collection.
        """
        return len(self.value)

    def __getitem__(self, index_or_key):
        """
        Returns the item corresponding to the given index or index_or_key.

        Parameters
        ----------
        index_or_key : int or str
            Index or key to the collection.

        Returns
        -------
        item : object
            Item corresponding to the given index or key.
        """
        return self.value[index_or_key]

    def get(self, index_or_key, default=None, raw=False, render=False):
        """
        Returns the raw value from the collection. If the value is str, returns
        TemplateString which is bound to a namespace and can be rendered later.

        Parameters
        ----------
        index_or_key : int or str
            Index or key to the collection.
        default : object
            Default value.
        raw :True
            Whether to get row collection or ``ConfigCollection``.
        render : bool
            Whether to render template strings with the bound namespace.

        Returns
        -------
        item : object
            Raw item corresponding to the given index or key.
        """
        if raw:
            return self.get_raw(index_or_key, default=default, render=render)
        try:
            value = self.value[index_or_key]
            if isinstance(value, str):
                ts = TemplateString(value, self.namespace)
                return ts.render() if render else ts
            else:
                return value
        except (IndexError, KeyError):
            return default

    def get_raw(self, index_or_key, default=_NO_DEFAULT, render=True):
        """
        Returns the raw value from the collection. If the value is str, returns
        TemplateString which is bound to a namespace and can be rendered later.

        Parameters
        ----------
        index_or_key : int or str
            Index or key to the collection.
        default : object
            Default value.
        render : bool
            Whethere to render template strings with the bound namespace.

        Returns
        -------
        item : object
            Raw item corresponding to the given index or key.
        """
        try:
            value = self.value[index_or_key]
            if isinstance(value, ConfigDict):
                return {k: value.get_raw(k, render=render) for k in value}
            elif isinstance(value, ConfigList):
                return [value.get_raw(i, render=render) for i in range(len(value))]
            elif isinstance(value, str):
                ts = TemplateString(value, self.namespace)
                return ts.render() if render else ts
            else:
                return value
        except (IndexError, KeyError):
            if default is _NO_DEFAULT:
                raise
            return default

    def raw(self, render=False):
        """
        Returns the raw contents of the collection.

        Returns
        -------
        raw : list or dict
            Raw contents.
        render : bool
            Whethere to render template strings with the bound namespace.
        """
        raise NotImplementedError()


class ConfigList(ConfigCollection):
    """
    Configuration value as a list.
    """

    def __init__(self, value=None, namespace=None):
        """
        Initializes ConfigList.

        Parameters
        ----------
        value : list
            The value content.
        namespace : dict
            Namespace for string interpolation.
        """
        super().__init__(namespace)

        self.value = [ConfigValue.create(v, namespace=namespace) for v in value or []]

    def raw(self, render=False):
        """
        Returns the raw contents of the collection.

        Returns
        -------
        raw : list
            Raw contents.
        render : bool
            Whethere to render template strings with the bound namespace.
        """
        return [self.get_raw(i, render=render) for i in range(len(self.value))]


class ConfigDict(ConfigCollection):
    """
    Configuration value as a dict.
    """

    def __init__(self, value=None, namespace=None):
        """
        Initializes ConfigList.

        Parameters
        ----------
        value : dict
            The value content.
        namespace : dict
            Namespace for string interpolation.
        """
        super().__init__(namespace)

        self.value = {k: ConfigValue.create(v, namespace=namespace)
                      for k, v in (value or {}).items()}

    def __getattr__(self, attr):
        """
        Accesses a value like an attribute (``obj.dict_key``).

        Parameters
        ----------
        attr : object
            Dict key.
        """
        if attr not in self.value:
            raise AttributeError('{!r} object has no attribute {!r}'
                                 .format(type(self).__name__, attr))
        return self.value[attr]

    def keys(self):
        """
        Returns keys of the dict.

        Returns
        -------
        keys : dict_keys
            Keys of the dict.
        """
        return self.value.keys()

    def values(self):
        """
        Returns values of the dict.

        Returns
        -------
        values : generator
            Values of the dict.
        """
        return self.value.values()

    def items(self):
        """
        Returns pairs of key and value.

        Returns
        -------
        items : generator
            Paris of key and value.
        """
        return self.value.items()

    def raw(self, render=False):
        """
        Returns the raw contents of the collection.

        Returns
        -------
        raw : dict
            Raw contents.
        render : bool
            Whethere to render template strings with the bound namespace.
        """
        return {k: self.get_raw(k, render=render) for k in self.value}
