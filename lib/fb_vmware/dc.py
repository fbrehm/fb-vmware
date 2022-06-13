#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 by Frank Brehm, Berlin
@summary: The module for capsulating a VSphere datacenter object.
"""
from __future__ import absolute_import

# Standard modules
import logging

# Third party modules
from pyVmomi import vim

from fb_tools.common import pp
from fb_tools.xlate import format_list

# Own modules
from .obj import VsphereObject, DEFAULT_OBJ_STATUS

from .xlate import XLATOR

__version__ = '0.4.0'
LOG = logging.getLogger(__name__)

DEFAULT_HOST_FOLDER = 'host'
DEFAULT_VM_FOLDER = 'vm'
DEFAULT_DS_FOLDER = 'datastore'
DEFAULT_NETWORK_FOLDER = 'network'

_ = XLATOR.gettext


# =============================================================================
class VsphereDatacenter(VsphereObject):
    """
    Class for a VSphere Datacenter object.
    """

    # -------------------------------------------------------------------------
    def __init__(
        self, appname=None, verbose=0, version=__version__, base_dir=None, initialized=None,
            name=None, status=DEFAULT_OBJ_STATUS, config_status=DEFAULT_OBJ_STATUS,
            ds_folder=DEFAULT_DS_FOLDER, host_folder=DEFAULT_HOST_FOLDER,
            network_folder=DEFAULT_NETWORK_FOLDER, vm_folder=DEFAULT_VM_FOLDER,
            default_hw_version_key=None, max_hw_version_key=None):

        self.repr_fields = (
            'name', 'obj_type', 'name_prefix', 'status', 'config_status',
            'appname', 'verbose', 'version')

        self._host_folder = DEFAULT_HOST_FOLDER
        self._vm_folder = DEFAULT_VM_FOLDER
        self._ds_folder = DEFAULT_DS_FOLDER
        self._network_folder = DEFAULT_NETWORK_FOLDER
        self._default_hw_version_key = None
        self._max_hw_version_key = None

        super(VsphereDatacenter, self).__init__(
            name=name, obj_type='vsphere_datacenter', name_prefix="dc", status=status,
            config_status=config_status, appname=appname, verbose=verbose,
            version=version, base_dir=base_dir)

        self._ds_folder = ds_folder
        self._host_folder = host_folder
        self._network_folder = network_folder
        self._vm_folder = vm_folder
        self._default_hw_version_key = default_hw_version_key
        self._max_hw_version_key = max_hw_version_key

        if initialized is not None:
            self.initialized = initialized

    # -------------------------------------------------------------------------
    @property
    def ds_folder(self):
        """Name of the Folder for datastores and datastore clusters."""
        return self._ds_folder

    # -------------------------------------------------------------------------
    @property
    def host_folder(self):
        """Name of the Folder for hosts and compute resources."""
        return self._host_folder

    # -------------------------------------------------------------------------
    @property
    def network_folder(self):
        """Name of the Folder for networks."""
        return self._network_folder

    # -------------------------------------------------------------------------
    @property
    def vm_folder(self):
        """Name of the Folder for VMs."""
        return self._vm_folder

    # -------------------------------------------------------------------------
    @property
    def default_hw_version_key(self):
        """Key for Default Hardware Version used on this datacenter."""
        return self._default_hw_version_key

    # -------------------------------------------------------------------------
    @property
    def max_hw_version_key(self):
        """Key for Maximum Hardware Version used on this datacenter."""
        return self._max_hw_version_key

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(VsphereDatacenter, self).as_dict(short=short)
        res['ds_folder'] = self.ds_folder
        res['host_folder'] = self.host_folder
        res['network_folder'] = self.network_folder
        res['vm_folder'] = self.vm_folder
        res['default_hw_version_key'] = self.default_hw_version_key
        res['max_hw_version_key'] = self.max_hw_version_key

        return res

    # -------------------------------------------------------------------------
    def __copy__(self):

        return VsphereDatacenter(
            appname=self.appname, verbose=self.verbose, base_dir=self.base_dir,
            initialized=self.initialized, name=self.name,
            status=self.status, config_status=self.config_status,
            default_hw_version_key=self.default_hw_version_key,
            max_hw_version_key=self.max_hw_version_key)

    # -------------------------------------------------------------------------
    def __eq__(self, other):

        if self.verbose > 4:
            LOG.debug(_("Comparing {} objects ...").format(self.__class__.__name__))

        if not isinstance(other, VsphereDatacenter):
            return False

        if self.name != other.name:
            return False

        return True

    # -------------------------------------------------------------------------
    @classmethod
    def from_summary(cls, data, appname=None, verbose=0, base_dir=None, test_mode=False):

        if verbose > 3:
            LOG.debug("Creating {} object by data:".format(cls.__name__) + '\n' + pp(data))

        if test_mode:

            necessary_fields = (
                'name', 'overallStatus', 'configStatus', 'datastoreFolder', 'hostFolder',
                'networkFolder', 'vmFolder')
            named_fields = ('datastoreFolder', 'hostFolder', 'networkFolder', 'vmFolder')

            failing_fields = []

            for field in necessary_fields:
                if not hasattr(data, field):
                    failing_fields.append(field)

            for field in named_fields:
                if hasattr(data, field):
                    attr = getattr(data, field)
                    if not hasattr(attr, 'name'):
                        failing_fields.append(field + '.name')

            if len(failing_fields):
                msg = _(
                    "The given parameter {p!r} on calling method {m}() has failing "
                    "attributes").format(p='data', m='from_summary')
                msg += ': ' + format_list(failing_fields, do_repr=True)
                raise AssertionError(msg)

        else:
            if not isinstance(data, vim.Datacenter):
                msg = _(
                    "Parameter {t!r} must be a {e} object, a {v} object was given "
                    "instead.").format(t='data', e='vim.Datacenter', v=data.__class__.__qualname__)
                raise TypeError(msg)

        params = {
            'appname': appname,
            'verbose': verbose,
            'base_dir': base_dir,
            'initialized': True,
            'name': data.name,
            'status': data.overallStatus,
            'config_status': data.configStatus,
            'ds_folder': data.datastoreFolder.name,
            'host_folder': data.hostFolder.name,
            'network_folder': data.networkFolder.name,
            'vm_folder': data.vmFolder.name,
            'default_hw_version_key': None,
            'max_hw_version_key': None,
        }

        if hasattr(data, 'configuration'):
            if hasattr(data.configuration, 'defaultHardwareVersionKey'):
                params['default_hw_version_key'] = data.configuration.defaultHardwareVersionKey
            if hasattr(data.configuration, 'maximumHardwareVersionKey'):
                params['max_hw_version_key'] = data.configuration.maximumHardwareVersionKey

        if verbose > 2:
            LOG.debug(_("Creating {} object from:").format(cls.__name__) + '\n' + pp(params))

        dc = cls(**params)

        return dc


# =============================================================================

if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
