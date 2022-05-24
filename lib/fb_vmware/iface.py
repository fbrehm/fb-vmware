#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 by Frank Brehm, Berlin
@summary: The module for a VSphere network object.
"""
from __future__ import absolute_import

# Standard modules
import logging

# Third party modules
from pyVmomi import vim

from fb_tools.common import pp, RE_MAC_ADRESS
from fb_tools.obj import FbBaseObject
from fb_tools.xlate import format_list

# Own modules
from .errors import VSphereNameError

from .xlate import XLATOR


__version__ = '1.2.1'
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext


# =============================================================================
class VsphereVmInterface(FbBaseObject):

    # -------------------------------------------------------------------------
    def __init__(
        self, appname=None, verbose=0, version=__version__, base_dir=None, initialized=None,
            name=None, network=None, network_name=None, mac_address=None, summary=None):

        self.repr_fields = (
            'name', 'network_name', 'mac_address', 'summary', 'appname', 'verbose')

        self._name = None
        self.network = None
        self._network_name = None
        self._mac_address = None
        self._summary = None

        super(VsphereVmInterface, self).__init__(
            appname=appname, verbose=verbose, version=version, base_dir=base_dir)

        self.name = name
        self.mac_address = mac_address

        if network:
            if not isinstance(network, vim.Network):
                msg = _("Parameter {t!r} must be a {e}, {v!r} was given.").format(
                    t='network', e='vim.Network', v=network)
                raise TypeError(msg)
            self._network = network

        self.network_name = network_name
        self.summary = summary

    # -----------------------------------------------------------
    @property
    def obj_type(self):
        """The type of the VSphere object."""
        return 'vsphere_vm_interface'

    # -----------------------------------------------------------
    @property
    def name(self):
        """The name of the interface."""
        return self._name

    @name.setter
    def name(self, value):

        oname = self.obj_type + '.name'

        if value is None:
            raise VSphereNameError(value, oname)

        val = value.strip()
        if val == '':
            raise VSphereNameError(value, oname)

        self._name = val

    # -----------------------------------------------------------
    @property
    def network_name(self):
        """The name of the network of the interface."""
        return self._network_name

    @network_name.setter
    def network_name(self, value):
        oname = self.obj_type + '.network_name'

        if value is None:
            raise VSphereNameError(value, oname)
        val = value.strip()
        if val == '':
            raise VSphereNameError(value, oname)

        self._network_name = val

    # -----------------------------------------------------------
    @property
    def mac_address(self):
        """The Mac-Address of the interface."""
        return self._mac_address

    @mac_address.setter
    def mac_address(self, value):
        if value is None:
            self._mac_address = None
            return
        val = value.strip()
        if val == '':
            self._mac_address = None
            return
        if not RE_MAC_ADRESS.match(val):
            msg = _("Invalid MAC address {!r} for interface given.").format(value)
            raise ValueError(msg)

        self._mac_address = val.lower()

    # -----------------------------------------------------------
    @property
    def summary(self):
        """The Mac-Address of the interface."""
        return self._summary

    @summary.setter
    def summary(self, value):
        if value is None:
            self._summary = None
            return
        val = value.strip()
        if val == '':
            self._summary = None
            return
        self._summary = val

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(VsphereVmInterface, self).as_dict(short=short)
        res['name'] = self.name
        res['obj_type'] = self.obj_type
        res['network_name'] = self.network_name
        res['mac_address'] = self.mac_address
        res['summary'] = self.summary

        return res

    # -------------------------------------------------------------------------
    def __str__(self):
        """
        Typecasting function for translating object structure
        into a string

        @return: structure as string
        @rtype:  str
        """

        return pp(self.as_dict(short=True))


# =============================================================================

if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
