#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for capsulating a VSphere about info object.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import absolute_import

# Standard modules
import logging
import uuid


# Third party modules
from fb_tools.common import pp
from fb_tools.obj import FbBaseObject
from fb_tools.xlate import format_list

from pyVmomi import vim

# Own modules
from .xlate import XLATOR

__version__ = "1.0.1"
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext


# =============================================================================
class VsphereAboutInfo(FbBaseObject):
    """This is a wrapper for the about-information of a VMWare-VSphere center."""

    # -------------------------------------------------------------------------
    def __init__(
        self, appname=None, verbose=0, version=__version__, base_dir=None, initialized=None
    ):
        """Initialize the VsphereAboutInfo object."""
        self._api_type = None
        self._api_version = None
        self._name = None
        self._full_name = None
        self._vendor = None
        self._os_version = None
        self._os_type = None
        self._instance_uuid = None
        self._lic_prodname = None
        self._lic_prodversion = None

        super(VsphereAboutInfo, self).__init__(
            appname=appname, verbose=verbose, version=version, base_dir=base_dir
        )

        if initialized is not None:
            self.initialized = initialized

    # -----------------------------------------------------------
    @property
    def api_type(self):
        """Return the API type of the about object."""
        return self._api_type

    @api_type.setter
    def api_type(self, value):

        if value is None:
            self._api_type = None
            return
        v = str(value).strip()
        if v == "":
            self._api_type = None
        else:
            self._api_type = v

    # -----------------------------------------------------------
    @property
    def api_version(self):
        """Return the API version of the about object."""
        return self._api_version

    @api_version.setter
    def api_version(self, value):

        if value is None:
            self._api_version = None
            return
        v = str(value).strip()
        if v == "":
            self._api_version = None
        else:
            self._api_version = v

    # -----------------------------------------------------------
    @property
    def name(self):
        """Return the name of the about object."""
        return self._name

    @name.setter
    def name(self, value):

        if value is None:
            self._name = None
            return
        v = str(value).strip()
        if v == "":
            self._name = None
        else:
            self._name = v

    # -----------------------------------------------------------
    @property
    def full_name(self):
        """Return the full name of the about object."""
        return self._full_name

    @full_name.setter
    def full_name(self, value):

        if value is None:
            self._full_name = None
            return
        v = str(value).strip()
        if v == "":
            self._full_name = None
        else:
            self._full_name = v

    # -----------------------------------------------------------
    @property
    def vendor(self):
        """Return the vendor of the about object."""
        return self._vendor

    @vendor.setter
    def vendor(self, value):

        if value is None:
            self._vendor = None
            return
        v = str(value).strip()
        if v == "":
            self._vendor = None
        else:
            self._vendor = v

    # -----------------------------------------------------------
    @property
    def os_version(self):
        """Return the operating system version of the about object."""
        return self._os_version

    @os_version.setter
    def os_version(self, value):

        if value is None:
            self._os_version = None
            return
        v = str(value).strip()
        if v == "":
            self._os_version = None
        else:
            self._os_version = v

    # -----------------------------------------------------------
    @property
    def os_type(self):
        """Return the operating system type of the underlying OS."""
        return self._os_type

    @os_type.setter
    def os_type(self, value):

        if value is None:
            self._os_type = None
            return
        v = str(value).strip()
        if v == "":
            self._os_type = None
        else:
            self._os_type = v

    # -----------------------------------------------------------
    @property
    def instance_uuid(self):
        """Return the globally unique identifier associated with this service instance."""
        return self._instance_uuid

    @instance_uuid.setter
    def instance_uuid(self, value):

        if value is None:
            self._instance_uuid = None
            return
        v = str(value).strip()
        if v == "":
            self._instance_uuid = None
        else:
            try:
                v = uuid.UUID(v)
            except Exception:
                pass
            self._instance_uuid = v

    # -----------------------------------------------------------
    @property
    def lic_prodname(self):
        """Return the license product name."""
        return self._lic_prodname

    @lic_prodname.setter
    def lic_prodname(self, value):

        if value is None:
            self._lic_prodname = None
            return
        v = str(value).strip()
        if v == "":
            self._lic_prodname = None
        else:
            self._lic_prodname = v

    # -----------------------------------------------------------
    @property
    def lic_prodversion(self):
        """Return the license product version."""
        return self._lic_prodversion

    @lic_prodversion.setter
    def lic_prodversion(self, value):

        if value is None:
            self._lic_prodversion = None
            return
        v = str(value).strip()
        if v == "":
            self._lic_prodversion = None
        else:
            self._lic_prodversion = v

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transform the elements of the object into a dict.

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """
        res = super(VsphereAboutInfo, self).as_dict(short=short)
        res["api_type"] = self.api_type
        res["api_version"] = self.api_version
        res["name"] = self.name
        res["full_name"] = self.full_name
        res["vendor"] = self.vendor
        res["os_version"] = self.os_version
        res["os_type"] = self.os_type
        res["instance_uuid"] = self.instance_uuid
        res["lic_prodname"] = self.lic_prodname
        res["lic_prodversion"] = self.lic_prodversion

        return res

    # -------------------------------------------------------------------------
    @classmethod
    def from_summary(cls, data, appname=None, verbose=0, base_dir=None, test_mode=False):
        """Create a new VsphereAboutInfo object based on the data given from pyvmomi module."""
        if test_mode:

            necessary_fields = (
                "apiType",
                "apiVersion",
                "name",
                "fullName",
                "vendor",
                "version",
                "osType",
                "instanceUuid",
                "licenseProductName",
                "licenseProductVersion",
            )
            failing_fields = []

            for field in necessary_fields:
                if not hasattr(data, field):
                    failing_fields.append(field)

            if len(failing_fields):
                msg = _(
                    "The given parameter {p!r} on calling method {m}() has failing " "attributes"
                ).format(p="data", m="from_summary")
                msg += ": " + format_list(failing_fields, do_repr=True)
                raise AssertionError(msg)

        else:
            if not isinstance(data, vim.AboutInfo):
                msg = _(
                    "Parameter {t!r} must be a {e} object, a {v} object was given " "instead."
                ).format(t="data", e="vim.AboutInfo", v=data.__class__.__qualname__)
                raise TypeError(msg)

        params = {
            "appname": appname,
            "verbose": verbose,
            "base_dir": base_dir,
            "initialized": False,
        }

        if verbose > 2:
            LOG.debug(_("Creating {} object from:").format(cls.__name__) + "\n" + pp(params))
        info = cls(**params)

        #        'about': (vim.AboutInfo) {
        #               dynamicType = <unset>,
        #               dynamicProperty = (vmodl.DynamicProperty) [],
        #               name = 'VMware vCenter Server',
        #               fullName = 'VMware vCenter Server 6.5.0 build-8024368',
        #               vendor = 'VMware, Inc.',
        #               version = '6.5.0',
        #               build = '8024368',
        #               localeVersion = 'INTL',
        #               localeBuild = '000',
        #               osType = 'linux-x64',
        #               productLineId = 'vpx',
        #               apiType = 'VirtualCenter',
        #               apiVersion = '6.5',
        #               instanceUuid = 'ea1b28ca-0d17-4292-ab04-189e57ec9629',
        #               licenseProductName = 'VMware VirtualCenter Server',
        #               licenseProductVersion = '6.0'
        #        },

        info.api_type = data.apiType
        info.api_version = data.apiVersion
        info.name = data.name
        info.full_name = data.fullName
        info.vendor = data.vendor
        info.os_version = data.version
        info.os_type = data.osType
        info.instance_uuid = data.instanceUuid
        info.lic_prodname = data.licenseProductName
        info.lic_prodversion = data.licenseProductVersion

        info.initialized = True

        if verbose > 2:
            LOG.debug(_("Created {} object:").format(cls.__name__) + "\n" + pp(info.as_dict()))

        return info

    # -------------------------------------------------------------------------
    def __copy__(self):
        """Return a new VsphereAboutInfo object with data from current object copied in."""
        info = VsphereAboutInfo(
            appname=self.appname, verbose=self.verbose, base_dir=self.base_dir, initialized=False
        )

        info.api_type = self.api_type
        info.api_version = self.api_version
        info.name = self.name
        info.full_name = self.full_name
        info.vendor = self.vendor
        info.os_version = self.os_version
        info.os_type = self.os_type
        info.instance_uuid = self.instance_uuid
        info.lic_prodname = self.lic_prodname
        info.lic_prodversion = self.lic_prodversion

        info.initialized = self.initialized

        return info


# =============================================================================
if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
