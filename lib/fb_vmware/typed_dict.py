#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The base module for a typed dict object.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import absolute_import

# Standard modules
import functools
import logging
try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

# Third party modules
from fb_tools.obj import FbGenericBaseObject

# Own modules
from .xlate import XLATOR

__version__ = '0.1.1'
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext


# =============================================================================
class TypedDict(MutableMapping, FbGenericBaseObject):
    """
    A dictionary containing typed objects.

    It works like a dict.
    """

    msg_invalid_item_type = _('Invalid item type {got!r} to set, only {expected} allowed.')
    msg_none_type_error = _('None type as key is not allowed.')
    msg_empty_key_error = _('Empty key {!r} is not allowed.')
    msg_no_typed_object = _('Object {got!r} is not a {expected} object.')

    value_class = FbGenericBaseObject

    # -------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Initialize a TypedDict object."""
        self._map = {}

        for arg in args:
            self.append(arg)

    # -------------------------------------------------------------------------
    def check_key_by_item(self, key, item):
        """
        Check the key by the given item.

        Maybe overridden.
        Should throw a KeyError, if key is not valid.
        """
        return True

    # -------------------------------------------------------------------------
    def _set_item(self, key, item):
        """
        Set the given Network to the given key.

        The key must be identic to the name of the network.
        """
        if not isinstance(item, self.value_class):
            msg = self.msg_invalid_item_type.format(
                got=item.__class__.__name__, expected=self.value_class.__name__)
            raise TypeError(msg)

        self.check_key_by_item(key, item)

        stripped_key = str(key).strip()
        if stripped_key == '':
            raise ValueError(self.msg_empty_key_error.format(key))

        self._map[stripped_key] = item

    # -------------------------------------------------------------------------
    def get_key_from_item(self, item):
        """
        Return a usable key from the item.

        Maybe overridden.
        """
        return str(hash(item)).strip()

    # -------------------------------------------------------------------------
    def append(self, item):
        """Set the given network in the current dict with its name as key."""
        if not isinstance(item, self.value_class):
            msg = self.msg_invalid_item_type.format(
                got=item.__class__.__name__, expected=self.value_class.__name__)
            raise TypeError(msg)

        key = self.get_key_from_item(item)
        self._set_item(key, item)

    # -------------------------------------------------------------------------
    def _get_item(self, key):

        if key is None:
            raise TypeError(self.msg_none_type_error)

        stripped_key = str(key).strip()
        if stripped_key == '':
            raise ValueError(self.msg_empty_key_error.format(key))

        return self._map[key]

    # -------------------------------------------------------------------------
    def get(self, key):
        """Get the item from dict by its key."""
        return self._get_item(key)

    # -------------------------------------------------------------------------
    def _del_item(self, key, strict=True):

        if key is None:
            raise TypeError(self.msg_none_type_error)

        stripped_key = str(key).strip()
        if stripped_key == '':
            raise ValueError(self.msg_empty_key_error.format(key))

        if not strict and stripped_key not in self._map:
            return

        del self._map[key]

    # -------------------------------------------------------------------------
    # The next five methods are requirements of the ABC.
    def __setitem__(self, key, item):
        """Set the given item in the current dict by key."""
        self._set_item(key, item)

    # -------------------------------------------------------------------------
    def __getitem__(self, key):
        """Get the item from dict by the key."""
        return self._get_item(key)

    # -------------------------------------------------------------------------
    def __delitem__(self, key):
        """Remove the item from dict by the key."""
        self._del_item(key)

    # -------------------------------------------------------------------------
    def __iter__(self):
        """Iterate through item keys."""
        for key in self.keys():
            yield key

    # -------------------------------------------------------------------------
    def __len__(self):
        """Return the number of items in current dict."""
        return len(self._map)

    # -------------------------------------------------------------------------
    # The next methods aren't required, but nice for different purposes:
    def __str__(self):
        """Return simple dict representation of the mapping."""
        return str(self._map)

    # -------------------------------------------------------------------------
    def __repr__(self):
        """Transform into a string for reproduction."""
        return '{}, {}({})'.format(
            super(TypedDict, self).__repr__(),
            self.__class__.__name__,
            self._map)

    # -------------------------------------------------------------------------
    def __contains__(self, key):
        """Return whether the given item key is contained in current dict."""
        if key is None:
            raise TypeError(self.msg_none_type_error)

        stripped_key = str(key).strip()
        if stripped_key == '':
            raise ValueError(self.msg_empty_key_error.format(key))

        return stripped_key in self._map

    # -------------------------------------------------------------------------
    def compare(self, x, y):
        """Compare two items, used with functools for sorting. Maybe overridden."""
        if x is None and y is None:
            return 0
        if x is None:
            return -1
        if y is None:
            return 1

        x_s = str(x).lower()
        y_s = str(y).lower()

        if x_s < y_s:
            return -1
        if x_s > y_s:
            return 1
        return 0

    # -------------------------------------------------------------------------
    def keys(self):
        """Return all items of this dict in a sorted manner."""
        return sorted(
            self._map.keys(),
            key=functools.cmp_to_key(self.compare))

    # -------------------------------------------------------------------------
    def items(self):
        """Return tuples (key + item as tuple) of this dict in a sorted manner."""
        item_list = []

        for key in self.keys():
            item_list.append((key, self._map[key]))

        return item_list

    # -------------------------------------------------------------------------
    def values(self):
        """Return all items of this dict."""
        value_list = []
        for key in self.keys():
            value_list.append(self._map[key])
        return value_list

    # -------------------------------------------------------------------------
    def __eq__(self, other):
        """Magic method for using it as the '=='-operator."""
        if not isinstance(other, self.__class__):
            msg = self.msg_no_typed_object.format(
                got=other, expected=self.__class__.__name__)
            raise TypeError(msg)

        return self._map == other._map

    # -------------------------------------------------------------------------
    def __ne__(self, other):
        """Magic method for using it as the '!='-operator."""
        if not isinstance(other, self.__class__):
            msg = self.msg_no_typed_object.format(
                got=other, expected=self.__class__.__name__)
            raise TypeError(msg)

        return self._map != other._map

    # -------------------------------------------------------------------------
    def pop(self, key, *args):
        """Get the item by its name and remove it in dict."""
        if key is None:
            raise TypeError(self.msg_none_type_error)

        # key = self.get_key_from_item(item)
        if key == '':
            raise ValueError(self.msg_empty_key_error.format(key))

        return self._map.pop(key, *args)

    # -------------------------------------------------------------------------
    def popitem(self):
        """Remove and return a arbitrary (key and item) pair from the dictionary."""
        if not len(self._map):
            return None

        key = self.keys()[0]
        item = self._map[key]
        del self._map[key]
        return (key, item)

    # -------------------------------------------------------------------------
    def clear(self):
        """Remove all items from the dictionary."""
        self._map = {}

    # -------------------------------------------------------------------------
    def setdefault(self, key, default):
        """
        Return the item, if the key is in dict.

        If not, insert key with a value of default and return default.
        """
        if key is None:
            raise TypeError(self.msg_none_type_error)

        stripped_key = str(key).strip()
        if stripped_key == '':
            raise ValueError(self.msg_empty_key_error.format(key))

        if not isinstance(default, self.value_class):
            msg = self.msg_invalid_item_type.format(
                got=default.__class__.__name__, expected=self.value_class.__name__)
            raise TypeError(msg)

        if stripped_key in self._map:
            return self._map[stripped_key]

        self._set_item(stripped_key, default)
        return default

    # -------------------------------------------------------------------------
    def update(self, other):
        """Update the dict with the key/item pairs from other, overwriting existing keys."""
        if isinstance(other, self.__class__) or isinstance(other, dict):
            for key in other.keys():
                self._set_item(key, other[key])
            return

        for tokens in other:
            key = tokens[0]
            value = tokens[1]
            self._set_item(key, value)

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """Transform the elements of the object into a dict."""
        res = {}
        for key in self._map:
            res[key] = self._map[key].as_dict(short)
        return res

    # -------------------------------------------------------------------------
    def as_list(self, short=True):
        """Return a list with all items transformed to a dict."""
        res = []
        for key in self.keys():
            res.append(self._map[key].as_dict(short))
        return res


# =============================================================================
if __name__ == '__main__':

    pass

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
