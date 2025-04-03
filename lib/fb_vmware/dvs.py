#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for a VSphere Distributed Virtual Switch and a
          Distributed Virtual Port Group.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import absolute_import

# Standard modules
import logging
import re
try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

# Third party modules
from fb_tools.common import pp
from fb_tools.obj import FbGenericBaseObject
from fb_tools.xlate import format_list

from pyVmomi import vim

# Own modules
from .network import VsphereNetwork
from .obj import DEFAULT_OBJ_STATUS
from .obj import VsphereObject
from .xlate import XLATOR

__version__ = '0.2.1'
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext

# =============================================================================
class VsphereDVS(VsphereObject):
    """Wrapper class for a VSphere Distributed Virtual Switch (vim.DistributedVirtualSwitch)."""

    properties = [
        'contact_info',
        'contact_name',
        'create_time',
        'def_proxy_switch_max_num_ports',
        'description',
        'extension_key',
        'ip_address',
        'max_ports',
        'net_resource_mgmt_enabled',
        'num_hosts',
        'num_ports',
        'num_standalone_ports',
        'pnic_cap_ratio_reservation',
        'product_name',
        'product_vendor',
        'product_version',
        'uuid',
    ]

    prop_source = {
        'uuid': 'uuid',
    }

    prop_source_config = {
        'create_time': 'createTime',
        'def_proxy_switch_max_num_ports': 'defaultProxySwitchMaxNumPorts',
        'description': 'description',
        'extension_key': 'extensionKey',
        'ip_address': 'switchIpAddress',
        'max_ports': 'maxPorts',
        'name': 'name',
        'net_resource_mgmt_enabled': 'networkResourceManagementEnabled',
        'num_ports': 'numPorts',
        'num_standalone_ports': 'numStandalonePorts',
        'pnic_cap_ratio_reservation': 'pnicCapacityRatioForReservation',
    }

    prop_source_contact = {
        'contact_info': 'contact',
        'contact_name': 'name',
    }

    prop_source_product = {
        'product_name': 'name',
        'product_vendor': 'vendor',
        'product_version': 'version',
    }

    prop_source_summary = {
        'num_hosts': 'numHosts',
    }

    necessary_fields = [
        'uuid',
    ]

    necessary_config_fields = [
        'createTime',
        'maxPorts',
        'numPorts',
        'numStandalonePorts',
    ]

    repr_fields = ['name'] + properties + ['appname', 'verbose']

    # -------------------------------------------------------------------------
    def __init__(
            self, appname=None, verbose=0, version=__version__, base_dir=None, initialized=None,
            name=None, obj_type='vsphere_vds', name_prefix='vds', status=DEFAULT_OBJ_STATUS,
            config_status=DEFAULT_OBJ_STATUS, **kwargs):
        """Initialize a VsphereDVS object."""
        for prop in self.properties:
            setattr(self, '_' + prop, None)

        super(VsphereDVS, self).__init__(
            name=name, obj_type=obj_type, name_prefix=name_prefix, status=status,
            config_status=config_status, appname=appname, verbose=verbose,
            version=version, base_dir=base_dir)

        for argname in kwargs:
            if argname not in self.properties:
                msg = _('Invalid Argument {arg!r} on {what} given.').format(
                    arg=argname, what='VsphereDVS.init()')
                raise AttributeError(msg)
            if kwargs[argname] is not None:
                setattr(self, '_' + argname, kwargs[argname])

        if initialized is not None:
            self.initialized = initialized

        if self.verbose > 3:
            LOG.debug(_('Initialized Distributed Virtual Switch:') + '\n' + pp(self.as_dict()))

    # -----------------------------------------------------------
    @property
    def contact_info(self):
        """Return the contact information for the contact person of this VDS."""
        return self._contact_info

    # -----------------------------------------------------------
    @property
    def contact_name(self):
        """Return the name of the responsible person for this VDS."""
        return self._contact_name

    # -----------------------------------------------------------
    @property
    def create_time(self):
        """Return the creation date of this VDS."""
        return self._create_time

    # -----------------------------------------------------------
    @property
    def def_proxy_switch_max_num_ports(self):
        """Return the default host proxy switch maximum port number of this VDS."""
        return self._def_proxy_switch_max_num_ports

    # -----------------------------------------------------------
    @property
    def description(self):
        """Return the description of this VDS."""
        return self._description

    # -----------------------------------------------------------
    @property
    def extension_key(self):
        """
        Return the extension key of this VDS.

        This is the Key of the extension registered by the remote server that controls the switch. 
        """
        return self._extension_key

    # -----------------------------------------------------------
    @property
    def max_ports(self):
        """Return the maximum number of ports allowed in the switch of this VDS."""
        return self._max_ports

    # -----------------------------------------------------------
    @property
    def ip_address(self):
        """Return the IP address for the switch of this VDS."""
        return self._ip_address

    # -----------------------------------------------------------
    @property
    def net_resource_mgmt_enabled(self):
        """Return whether network I/O control is enabled on this VDS."""
        return self._net_resource_mgmt_enabled

    # -----------------------------------------------------------
    @property
    def num_hosts(self):
        """Return the number of hosts in this VDS."""
        return self._num_hosts

    # -----------------------------------------------------------
    @property
    def num_ports(self):
        """Return the current number of ports of this VDS."""
        return self._num_ports

    # -----------------------------------------------------------
    @property
    def num_standalone_ports(self):
        """Return the number of standalone ports in this VDS."""
        return self._num_standalone_ports

    # -----------------------------------------------------------
    @property
    def pnic_cap_ratio_reservation(self):
        """Return the percentage of physical nic link speed of this VDS."""
        return self._pnic_cap_ratio_reservation

    # -----------------------------------------------------------
    @property
    def product_name(self):
        """Return the short form of the product name of this VDS."""
        return self._product_name

    # -----------------------------------------------------------
    @property
    def product_vendor(self):
        """Return the name of the vendor of this product of this VDS."""
        return self._product_vendor

    # -----------------------------------------------------------
    @property
    def product_version(self):
        """Return the dot-separated version string of this VDS."""
        return self._product_version

    # -----------------------------------------------------------
    @property
    def uuid(self):
        """Return the UUID of this VDS."""
        return self._uuid

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transform the elements of the object into a dict.

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """
        res = super(VsphereDVS, self).as_dict(short=short)

        for prop in self.properties:
            res[prop] = getattr(self, prop)

        return res

    # -------------------------------------------------------------------------
    def __eq__(self, other):
        """Magic method for using it as the '=='-operator."""
        if self.verbose > 4:
            LOG.debug(_('Comparing {} objects ...').format(self.__class__.__name__))

        if not isinstance(other, VsphereDVS):
            return False

        if self.uuid != other.uuid:
            return False

        return True

    # -------------------------------------------------------------------------
    @classmethod
    def from_summary(cls, data, appname=None, verbose=0, base_dir=None, test_mode=False):
        """Create a new VsphereDVS object based on the data given from pyvmomi."""
        if test_mode:

            failing_fields = []

            for field in cls.necessary_fields:
                if not hasattr(data, field):
                    failing_fields.append(field)

            if hasattr(data, 'config'):
                for field in cls.necessary_config_fields:
                    if not hasattr(data.config, field):
                        failing_fields.append('config.' + field)
                if not hasattr(data.config, 'name'):
                    failing_fields.append('config.name')
            else:
                failing_fields.append('config')

            if not hasattr(data, 'summary'):
                failing_fields.append('summary')

            if len(failing_fields):
                msg = _(
                    'The given parameter {p!r} on calling method {m}() has failing '
                    'attributes').format(p='data', m='from_summary')
                msg += ': ' + format_list(failing_fields, do_repr=True)
                raise AssertionError(msg)

        else:
            if not isinstance(data, vim.DistributedVirtualSwitch):
                msg = _('Parameter {t!r} must be a {e}, {v} was given.').format(
                    t='data', e='vim.DistributedVirtualSwitch', v=data.__class__.__name__)
                raise TypeError(msg)

        params = {
            'appname': appname,
            'verbose': verbose,
            'base_dir': base_dir,
            'initialized': True,
        }

        for prop in cls.prop_source:
            prop_src = cls.prop_source[prop]
            value = getattr(data, prop_src, None)
            if value is not None:
                params[prop] = value

        for prop in cls.prop_source_config:
            prop_src = cls.prop_source_config[prop]
            value = getattr(data.config, prop_src, None)
            if value is not None:
                params[prop] = value

        for prop in cls.prop_source_contact:
            prop_src = cls.prop_source_contact[prop]
            value = getattr(data.config.contact, prop_src, None)
            if value is not None:
                params[prop] = value

        for prop in cls.prop_source_product:
            prop_src = cls.prop_source_product[prop]
            value = getattr(data.config.productInfo, prop_src, None)
            if value is not None:
                params[prop] = value

        for prop in cls.prop_source_summary:
            prop_src = cls.prop_source_summary[prop]
            value = getattr(data.summary, prop_src, None)
            if value is not None:
                params[prop] = value

        if verbose > 1:
            if verbose > 2:
                LOG.debug(_('Creating {} object from:').format(cls.__name__) + '\n' + pp(params))
            else:
                LOG.debug(_('Creating {cls} object {name!r}.').format(
                    cls=cls.__name__, name=data.summary.name))

        vds = cls(**params)

        return vds


# =============================================================================
if __name__ == '__main__':

    pass

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
