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
        if isinstance(value, dict):
            return ConfigDict(value, namespace=namespace)
        elif isinstance(value, list):
            return ConfigList(value, namespace=namespace)
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

    def get(self, key, default=_NO_DEFAULT):
        """
        Returns the raw value from the collection. If the value is str, returns
        TemplateString which is bound to a namespace and can be rendered later.

        Parameters
        ----------
        index_or_key : int or str
            Index or key to the collection.
        default : object
            Default value.

        Returns
        -------
        item : object
            Raw item corresponding to the given index or key.
        """
        try:
            return self._get_raw(key)
        except (IndexError, KeyError):
            if default is _NO_DEFAULT:
                raise
            return default

    def _get_raw(self, index_or_key):
        """
        Returns the raw value from the collection. If the value is str, returns
        TemplateString which is bound to a namespace and can be rendered later.

        Parameters
        ----------
        index_or_key : int or str
            Index or key to the collection.

        Returns
        -------
        item : object
            Raw item corresponding to the given index or key.
        """
        value = self.value[index_or_key]
        if isinstance(value, ConfigDict):
            return {k: value.get(k) for k in value}
        elif isinstance(value, ConfigList):
            return [value.get(i) for i in range(len(value))]
        elif isinstance(value, str):
            return TemplateString(value, self.namespace)
        else:
            return value

    def raw(self):
        """
        Returns the raw contents of the collection.

        Returns
        -------
        raw : list or dict
            Raw contents.
        """
        raise NotImplementedError()


class ConfigList(ConfigCollection):
    """
    Configuration value as a list.
    """

    def __init__(self, value, namespace=None):
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

        self.value = [ConfigValue.create(v, namespace=namespace) for v in value]

    def raw(self):
        """
        Returns the raw contents of the collection.

        Returns
        -------
        raw : list
            Raw contents.
        """
        return [self._get_raw(i) for i in range(len(self.value))]


class ConfigDict(ConfigCollection):
    """
    Configuration value as a dict.
    """

    def __init__(self, value, namespace=None):
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
                      for k, v in value.items()}

    def __getattr__(self, attr):
        return self.get(attr)

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
        return (self.get(k) for k in self.value)

    def items(self):
        """
        Returns pairs of key and value.

        Returns
        -------
        items : generator
            Paris of key and value.
        """
        return ((k, self.get(k)) for k in self.value)

    def raw(self):
        """
        Returns the raw contents of the collection.

        Returns
        -------
        raw : dict
            Raw contents.
        """
        return {k: self._get_raw(k) for k in self.value}
