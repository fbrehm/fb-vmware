#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for a VSphere network object.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import absolute_import

# Standard modules
import functools
import ipaddress
import logging
import re
try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

# Third party modules
from fb_tools.common import pp, to_bool
from fb_tools.obj import FbGenericBaseObject
from fb_tools.xlate import format_list

from pyVmomi import vim

# Own modules
from .obj import DEFAULT_OBJ_STATUS
from .obj import VsphereObject
from .xlate import XLATOR

__version__ = '1.5.0'
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext

NETWORK = 'network'
DV_PORTGROUP = 'dv_portgroup'
OPAQUE_NETWORK = 'opaque_network'


# =============================================================================
class VsphereNetwork(VsphereObject):
    """Wrapper class for a Network definition in VSPhere (vim.Network)."""

    re_ipv4_name = re.compile(r'\s*((?:\d{1,3}\.){3}\d{1,3})_(\d+)\s*$')
    re_tf_name = re.compile(r'[^a-z0-9_]+', re.IGNORECASE)

    net_properties = [
        'accessible', 'ip_pool_id', 'ip_pool_name'
    ]

    repr_fields = (
        'name', 'obj_type', 'status', 'config_status', 'accessible',
        'ip_pool_id', 'ip_pool_name', 'appname', 'verbose')

    net_prop_source = {
        'status': 'overallStatus',
        'config_status': 'configStatus',
    }

    net_prop_source_summary = {
        'name': 'name',
        'accessible': 'accessible',
        'ip_pool_id': 'ipPoolId',
        'ip_pool_name': 'ipPoolName',
    }

    necessary_net_fields = ['summary', 'overallStatus', 'configStatus']
    necessary_net_summary_fields = ['name']

    warn_unassigned_net = True

    # -------------------------------------------------------------------------
    def __init__(
            self, appname=None, verbose=0, version=__version__, base_dir=None, initialized=None,
            name=None, obj_type='vsphere_network', name_prefix='net', status=DEFAULT_OBJ_STATUS,
            config_status=DEFAULT_OBJ_STATUS, **kwargs):
        """Initialize a VsphereNetwork object."""
        for prop in self.net_properties:
            setattr(self, '_' + prop, None)

        self._network = None

        super(VsphereNetwork, self).__init__(
            name=name, obj_type=obj_type, name_prefix=name_prefix, status=status,
            config_status=config_status, appname=appname, verbose=verbose,
            version=version, base_dir=base_dir)

        for argname in kwargs:
            if argname not in self.net_properties:
                msg = _('Invalid Argument {arg!r} on {what} given.').format(
                    arg=argname, what='VsphereNetwork.init()')
                raise AttributeError(msg)
            if kwargs[argname] is not None:
                setattr(self, argname, kwargs[argname])

        match = self.re_ipv4_name.search(self.name)
        if match:
            ip = '{a}/{m}'.format(a=match.group(1), m=match.group(2))
            if self.verbose > 3:
                LOG.debug(_('Trying to get IPv4 network {n!r} -> {i!r}.').format(
                    n=self.name, i=ip))

            try:
                net = ipaddress.ip_network(ip)
                self._network = net
            except ValueError:
                LOG.error(_('Could not get IP network from network name {!r}.').format(self.name))

        if not self.network:
            msg = _('Network {!r} has no IP network assigned.').format(self.name)
            if self.warn_unassigned_net:
                LOG.warning(msg)
            else:
                LOG.info(msg)

        if initialized is not None:
            self.initialized = initialized

        if self.verbose > 3:
            LOG.debug(_('Initialized network object:') + '\n' + pp(self.as_dict()))

    # -----------------------------------------------------------
    @property
    def accessible(self):
        """Return the connectivity status of this network."""
        return self._accessible

    @accessible.setter
    def accessible(self, value):
        self._accessible = to_bool(value)

    # -----------------------------------------------------------
    @property
    def ip_pool_id(self):
        """Return the Identifier of the associated IP pool."""
        return self._ip_pool_id

    @ip_pool_id.setter
    def ip_pool_id(self, value):
        self._ip_pool_id = value

    # -----------------------------------------------------------
    @property
    def ip_pool_name(self):
        """Return the name of the associated IP pool."""
        return self._ip_pool_name

    @ip_pool_name.setter
    def ip_pool_name(self, value):
        self._ip_pool_name = value

    # -----------------------------------------------------------
    @property
    def network(self):
        """Return the ipaddress network object associated with this network."""
        return self._network

    # -----------------------------------------------------------
    @property
    def gateway(self):
        """Return the IP address of the getaeway inside this network."""
        if not self.network:
            return None
        return self.network.network_address + 1

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transform the elements of the object into a dict.

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """
        res = super(VsphereNetwork, self).as_dict(short=short)

        for prop in self.net_properties:
            res[prop] = getattr(self, prop)

        res['network'] = self.network
        res['gateway'] = self.gateway

        return res

    # -------------------------------------------------------------------------
    @classmethod
    def from_summary(cls, data, appname=None, verbose=0, base_dir=None, test_mode=False):
        """Create a new VsphereNetwork object based on the data given from pyvmomi."""
        if test_mode:

            failing_fields = []

            for field in self.necessary_net_fields:
                if not hasattr(data, field):
                    failing_fields.append(field)

            if hasattr(data, 'summary'):
                for field in self.necessary_net_summary_fields:
                    if not hasattr(data.summary, field):
                        failing_fields.append('summary.' + field)

            if len(failing_fields):
                msg = _(
                    'The given parameter {p!r} on calling method {m}() has failing '
                    'attributes').format(p='data', m='from_summary')
                msg += ': ' + format_list(failing_fields, do_repr=True)
                raise AssertionError(msg)

        else:
            if not isinstance(data, vim.Network):
                msg = _('Parameter {t!r} must be a {e}, {v!r} was given.').format(
                    t='data', e='vim.Network', v=data)
                raise TypeError(msg)

        common_params = {
            'appname': appname,
            'verbose': verbose,
            'base_dir': base_dir,
            'initialized': True,
        }
        params = cls.get_init_params(data=data, verbose=verbose)
        params.update(common_params)

        if verbose > 1:
            if verbose > 3:
                LOG.debug(_('Creating {} object from:').format(cls.__name__) + '\n' + pp(params))
            else:
                LOG.debug(_('Creating {cls} object {name!r}.').format(
                    cls=cls.__name__, name=data.summary.name))

        net = cls(**params)

        return net

    # -------------------------------------------------------------------------
    @classmethod
    def get_init_params(cls, data, verbose=0):
        """Return a dict with all keys for init a new network object with from_summary()."""
        params = {}

        for prop in cls.net_prop_source:
            prop_src = cls.net_prop_source[prop]
            value = getattr(data, prop_src, None)
            if value is not None:
                params[prop] = value

        for prop in cls.net_prop_source_summary:
            prop_src = cls.net_prop_source_summary[prop]
            value = getattr(data.summary, prop_src, None)
            if value is not None:
                params[prop] = value

        return params

    # -------------------------------------------------------------------------
    def get_params_dict(self):
        """Return a dict with all keys for init a new network object with __init__."""

        params = {
            'appname': self.appname,
            'verbose': self.verbose,
            'base_dir': self.base_dir,
            'initialized': self.initialized,
            'name': self.name,
            'obj_type': self.obj_type,
            'name_prefix': self.name_prefix,
            'status': self.status,
        }
        for prop in self.net_properties:
            val = getattr(self, prop, None)
            params[prop] = val

        return params

    # -------------------------------------------------------------------------
    def __copy__(self):
        """Return a new VsphereNetwork as a deep copy of the current object."""
        params = self.get_params_dict()

        return VsphereNetwork(**params)

    # -------------------------------------------------------------------------
    def __eq__(self, other):
        """Magic method for using it as the '=='-operator."""
        if self.verbose > 4:
            LOG.debug(_('Comparing {} objects ...').format(self.__class__.__name__))

        if not isinstance(other, VsphereNetwork):
            return False

        if self.__class__.__name__ != other.__class__.__name__:
            return False

        if self.name != other.name:
            return False

        return True


# =============================================================================
class VsphereNetworkDict(MutableMapping, FbGenericBaseObject):
    """
    A dictionary containing VsphereNetwork objects.

    It works like a dict.
    """

    msg_invalid_net_type = _('Invalid item type {{!r}} to set, only {} allowed.').format(
        'VsphereNetwork')
    msg_key_not_name = _('The key {k!r} must be equal to the network name {n!r}.')
    msg_none_type_error = _('None type as key is not allowed.')
    msg_empty_key_error = _('Empty key {!r} is not allowed.')
    msg_no_net_dict = _('Object {{!r}} is not a {} object.').format('VsphereNetworkDict')

    # -------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Initialize a VsphereNetworkDict object."""
        self._map = {}

        for arg in args:
            self.append(arg)

    # -------------------------------------------------------------------------
    def _set_item(self, key, net):
        """
        Set the given Network to the given key.

        The key must be identic to the name of the network.
        """
        if not isinstance(net, VsphereNetwork):
            raise TypeError(self.msg_invalid_net_type.format(net.__class__.__name__))

        net_name = net.name
        if net_name != key:
            raise KeyError(self.msg_key_not_name.format(k=key, n=net_name))

        if net_name in self._map and self._map[net_name].nw_type == DV_PORTGROUP:
            return

        self._map[net_name] = net

    # -------------------------------------------------------------------------
    def append(self, net):
        """Set the given network in the current dict with its name as key."""
        if not isinstance(net, VsphereNetwork):
            raise TypeError(self.msg_invalid_net_type.format(net.__class__.__name__))
        self._set_item(net.name, net)

    # -------------------------------------------------------------------------
    def _get_item(self, key):

        if key is None:
            raise TypeError(self.msg_none_type_error)

        net_name = str(key).strip()
        if net_name == '':
            raise ValueError(self.msg_empty_key_error.format(key))

        return self._map[net_name]

    # -------------------------------------------------------------------------
    def get(self, key):
        """Get the network from dict by its name."""
        return self._get_item(key)

    # -------------------------------------------------------------------------
    def _del_item(self, key, strict=True):

        if key is None:
            raise TypeError(self.msg_none_type_error)

        net_name = str(key).strip()
        if net_name == '':
            raise ValueError(self.msg_empty_key_error.format(key))

        if not strict and net_name not in self._map:
            return

        del self._map[net_name]

    # -------------------------------------------------------------------------
    # The next five methods are requirements of the ABC.
    def __setitem__(self, key, value):
        """Set the given network in the current dict by key."""
        self._set_item(key, value)

    # -------------------------------------------------------------------------
    def __getitem__(self, key):
        """Get the network from dict by the key."""
        return self._get_item(key)

    # -------------------------------------------------------------------------
    def __delitem__(self, key):
        """Remove the network from dict by the key."""
        self._del_item(key)

    # -------------------------------------------------------------------------
    def __iter__(self):
        """Iterate through network names as keys."""
        for net_name in self.keys():
            yield net_name

    # -------------------------------------------------------------------------
    def __len__(self):
        """Return the number of networks in current dict."""
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
            super(VsphereNetworkDict, self).__repr__(),
            self.__class__.__name__,
            self._map)

    # -------------------------------------------------------------------------
    def __contains__(self, key):
        """Return whether the given network name is contained in current dict as a key."""
        if key is None:
            raise TypeError(self.msg_none_type_error)

        net_name = str(key).strip()
        if net_name == '':
            raise ValueError(self.msg_empty_key_error.format(key))

        return net_name in self._map

    # -------------------------------------------------------------------------
    def keys(self):
        """Return all network names of this dict in a sorted manner."""
        def netsort(x, y):
            net_x = self[x]
            net_y = self[y]
            if net_x.network is None and net_y.network is None:
                return (
                    (net_x.name.lower() > net_y.name.lower()) - (
                        net_x.name.lower() < net_y.name.lower()))
            if net_x.network is None:
                return -1
            if net_y.network is None:
                return 1
            if net_x.network < net_y.network:
                return -1
            if net_x.network > net_y.network:
                return 1
            return 0

        return sorted(self._map.keys(), key=functools.cmp_to_key(netsort))

    # -------------------------------------------------------------------------
    def items(self):
        """Return tuples (network name + object as tuple) of this dict in a sorted manner."""
        item_list = []

        for net_name in self.keys():
            item_list.append((net_name, self._map[net_name]))

        return item_list

    # -------------------------------------------------------------------------
    def values(self):
        """Return all network objects of this dict."""
        value_list = []
        for net_name in self.keys():
            value_list.append(self._map[net_name])
        return value_list

    # -------------------------------------------------------------------------
    def __eq__(self, other):
        """Magic method for using it as the '=='-operator."""
        if not isinstance(other, VsphereNetworkDict):
            raise TypeError(self.msg_no_net_dict.format(other))

        return self._map == other._map

    # -------------------------------------------------------------------------
    def __ne__(self, other):
        """Magic method for using it as the '!='-operator."""
        if not isinstance(other, VsphereNetworkDict):
            raise TypeError(self.msg_no_net_dict.format(other))

        return self._map != other._map

    # -------------------------------------------------------------------------
    def pop(self, key, *args):
        """Get the network by its name and remove it in dict."""
        if key is None:
            raise TypeError(self.msg_none_type_error)

        net_name = str(key).strip()
        if net_name == '':
            raise ValueError(self.msg_empty_key_error.format(key))

        return self._map.pop(net_name, *args)

    # -------------------------------------------------------------------------
    def popitem(self):
        """Remove and return a arbitrary (network name and object) pair from the dictionary."""
        if not len(self._map):
            return None

        net_name = self.keys()[0]
        net = self._map[net_name]
        del self._map[net_name]
        return (net_name, net)

    # -------------------------------------------------------------------------
    def clear(self):
        """Remove all items from the dictionary."""
        self._map = {}

    # -------------------------------------------------------------------------
    def setdefault(self, key, default):
        """
        Return the network, if the key is in dict.

        If not, insert key with a value of default and return default.
        """
        if key is None:
            raise TypeError(self.msg_none_type_error)

        net_name = str(key).strip()
        if net_name == '':
            raise ValueError(self.msg_empty_key_error.format(key))

        if not isinstance(default, VsphereNetwork):
            raise TypeError(self.msg_invalid_net_type.format(default.__class__.__name__))

        if net_name in self._map:
            return self._map[net_name]

        self._set_item(net_name, default)
        return default

    # -------------------------------------------------------------------------
    def update(self, other):
        """Update the dict with the key/value pairs from other, overwriting existing keys."""
        if isinstance(other, VsphereNetworkDict) or isinstance(other, dict):
            for net_name in other.keys():
                self._set_item(net_name, other[net_name])
            return

        for tokens in other:
            key = tokens[0]
            value = tokens[1]
            self._set_item(key, value)

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """Transform the elements of the object into a dict."""
        res = {}
        for net_name in self._map:
            res[net_name] = self._map[net_name].as_dict(short)
        return res

    # -------------------------------------------------------------------------
    def as_list(self, short=True):
        """Return a list with all networks transformed to a dict."""
        res = []
        for net_name in self.keys():
            res.append(self._map[net_name].as_dict(short))
        return res

    # -------------------------------------------------------------------------
    def get_network_for_ip(self, *ips):
        """
        Search a fitting network for the give IP addresses.

        The name of the first matching network for the first IP address, which will
        have a match, will be returned.
        """
        for ip in ips:
            if not ip:
                continue
            LOG.debug(_('Searching VSphere network for address {} ...').format(ip))
            ipa = ipaddress.ip_address(ip)

            for net_name in self.keys():
                net = self[net_name]
                if net.network and ipa in net.network:
                    LOG.debug(_('Found network {n!r} for IP {i}.').format(
                        n=net_name, i=ip))
                    return net_name

            LOG.debug(_('Could not find VSphere network for IP {}.').format(ip))

        ips_str = ', '.join((str(x) for x in list(filter(bool, ips))))
        LOG.error(_('Could not find VSphere network for IP addresses {}.').format(ips_str))
        return None


# =============================================================================
if __name__ == '__main__':

    pass

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
