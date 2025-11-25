#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for a vSphere host portgroup object.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import absolute_import

# Standard modules
import copy
import logging

try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence

# Third party modules
from fb_tools.common import pp

# from fb_tools.common import to_bool
from fb_tools.obj import FbBaseObject
from fb_tools.xlate import format_list

from pyVmomi import vim

# Own modules
from .xlate import XLATOR

__version__ = "1.0.1"
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext


# =============================================================================
class VsphereHostPortgroup(FbBaseObject):
    """This is a wrapeer for a vim.host.PortGroup object."""

    # -------------------------------------------------------------------------
    def __init__(
        self,
        appname=None,
        verbose=0,
        version=__version__,
        base_dir=None,
        initialized=None,
        name=None,
        vlan_id=None,
        vswitch_name=None,
        hostname=None,
    ):
        """Initialize a VsphereHostPortgroup object."""
        self._name = None
        self._vlan_id = None
        self._vswitch_name = None
        self._hostname = None

        super(VsphereHostPortgroup, self).__init__(
            appname=appname, verbose=verbose, version=version, base_dir=base_dir, initialized=False
        )

        self.name = name
        self.vlan_id = vlan_id
        self.vswitch_name = vswitch_name
        self.hostname = hostname

        if initialized is not None:
            self.initialized = initialized

    # -----------------------------------------------------------
    @property
    def name(self):
        """Return the name of the port group."""
        return self._name

    @name.setter
    def name(self, value):
        if value is None:
            self._name = None
            return
        v = str(value).strip()
        if v == "":
            self._name = None
            return
        self._name = v

    # -----------------------------------------------------------
    @property
    def vlan_id(self):
        """Return the VLAN ID for ports using this port group."""
        return self._vlan_id

    @vlan_id.setter
    def vlan_id(self, value):
        if value is None:
            self._vlan_id = None
            return
        self._vlan_id = int(value)

    # -----------------------------------------------------------
    @property
    def vswitch_name(self):
        """Return the identifier of the virtual switch on which this port group is located."""
        return self._vswitch_name

    @vswitch_name.setter
    def vswitch_name(self, value):
        if value is None:
            self._vswitch_name = None
            return
        v = str(value).strip()
        if v == "":
            self._vswitch_name = None
            return
        self._vswitch_name = v

    # -----------------------------------------------------------
    @property
    def hostname(self):
        """Return the host name of the port group."""
        return self._hostname

    @hostname.setter
    def hostname(self, value):
        if value is None:
            self._hostname = None
            return
        v = str(value).strip().lower()
        if v == "":
            self._hostname = None
            return
        self._hostname = v

    # -------------------------------------------------------------------------
    def as_dict(self, short=True, bare=False):
        """
        Transform the elements of the object into a dict.

        @param short: don't include local properties in resulting dict.
        @type short: bool
        @param bare: don't include generic fields in returning dict
        @type bare: bool

        @return: structure as dict
        @rtype:  dict
        """
        if bare:
            res = {
                "name": self.name,
                "vlan_id": self.vlan_id,
                "vswitch_name": self.vswitch_name,
                "hostname": self.hostname,
            }
            return res

        res = super(VsphereHostPortgroup, self).as_dict(short=short)
        res["name"] = self.name
        res["vlan_id"] = self.vlan_id
        res["vswitch_name"] = self.vswitch_name
        res["hostname"] = self.hostname

        return res

    # -------------------------------------------------------------------------
    def __eq__(self, other):
        """Magic method for using it as the '=='-operator."""
        if self.verbose > 4:
            LOG.debug(_("Comparing {} objects ...").format(self.__class__.__name__))

        if not isinstance(other, VsphereHostPortgroup):
            return False

        if self.hostname != other.hostname:
            return False
        if self.name != other.name:
            return False

        return True

    # -------------------------------------------------------------------------
    def __copy__(self):
        """Return a new VsphereHostPortgroup as a deep copy of the current object."""
        group = VsphereHostPortgroup(
            appname=self.appname,
            verbose=self.verbose,
            base_dir=self.base_dir,
            initialized=self.initialized,
            name=self.name,
            vlan_id=self.vlan_id,
            vswitch_name=self.vswitch_name,
            hostname=self.hostname,
        )

        return group

    # -------------------------------------------------------------------------
    @classmethod
    def from_summary(
        cls, data, hostname=None, appname=None, verbose=0, base_dir=None, test_mode=False
    ):
        """Create a new VsphereHostPortgroup object based on the data given from pyvmomi."""
        if test_mode:

            failing_fields = []
            if not hasattr(data, "spec"):
                failing_fields.append("spec")
            else:
                for field in ("name", "vlanId", "vswitchName"):
                    failing_fields.append("spec." + field)

            if len(failing_fields):
                msg = _(
                    "The given parameter {p!r} on calling method {m}() has failing " "attributes"
                ).format(p="data", m="from_summary")
                msg += ": " + format_list(failing_fields, do_repr=True)
                raise AssertionError(msg)

        else:
            if not isinstance(data, vim.host.PortGroup):
                msg = _("Parameter {t!r} must be a {e}, {v!r} ({vt}) was given.").format(
                    t="data", e="vim.host.PortGroup", v=data, vt=data.__class__.__name__
                )
                raise TypeError(msg)

        params = {
            "appname": appname,
            "verbose": verbose,
            "base_dir": base_dir,
            "initialized": True,
            "name": data.spec.name,
            "vlan_id": data.spec.vlanId,
            "vswitch_name": data.spec.vswitchName,
            "hostname": hostname,
        }

        if verbose > 2:
            LOG.debug(_("Creating {} object from:").format(cls.__name__) + "\n" + pp(params))

        group = cls(**params)

        if verbose > 2:
            LOG.debug(_("Created {} object:").format(cls.__name__) + "\n" + pp(group.as_dict()))

        return group


# =============================================================================
class VsphereHostPortgroupList(FbBaseObject, MutableSequence):
    """A list containing VsphereHostPortgroup objects."""

    msg_no_portgroup = _("Invalid type {t!r} as an item of a {c}, only {o} objects are allowed.")

    # -------------------------------------------------------------------------
    def __init__(
        self,
        appname=None,
        verbose=0,
        version=__version__,
        base_dir=None,
        initialized=None,
        hostname=None,
        *groups,
    ):
        """Initialize a VsphereHostPortgroupList object."""
        self._list = []
        self._hostname = None

        super(VsphereHostPortgroupList, self).__init__(
            appname=appname, verbose=verbose, version=version, base_dir=base_dir, initialized=False
        )

        self.hostname = hostname

        for group in groups:
            self.append(group)

        if initialized is not None:
            self.initialized = initialized

    # -----------------------------------------------------------
    @property
    def hostname(self):
        """Return the host name of the port group list."""
        return self._hostname

    @hostname.setter
    def hostname(self, value):
        if value is None:
            self._hostname = None
            return
        v = str(value).strip().lower()
        if v == "":
            self._hostname = None
            return
        self._hostname = v

    # -------------------------------------------------------------------------
    def as_dict(self, short=True, bare=False):
        """
        Transform the elements of the object into a dict.

        @param short: don't include local properties in resulting dict.
        @type short: bool
        @param bare: don't include generic fields in returning dict
        @type bare: bool

        @return: structure as dict or list
        @rtype:  dict or list
        """
        if bare:
            res = []
            for group in self:
                res.append(group.as_dict(bare=True))
            return res

        res = super(VsphereHostPortgroupList, self).as_dict(short=short)
        res["hostname"] = self.hostname
        res["_list"] = []

        for group in self:
            res["_list"].append(group.as_dict(short=short))

        return res

    # -------------------------------------------------------------------------
    def __copy__(self):
        """Return a new VsphereHostPortgroupList as a deep copy of the current object."""
        new_list = self.__class__(
            appname=self.appname,
            verbose=self.verbose,
            base_dir=self.base_dir,
            hostname=self.hostname,
            initialized=False,
        )

        for group in self:
            new_list.append(copy.copy(group))

        new_list.initialized = self.initialized
        return new_list

    # -------------------------------------------------------------------------
    def index(self, group, *args):
        """Return the numeric index of the given port group in current list."""
        i = None
        j = None

        if len(args) > 0:
            if len(args) > 2:
                raise TypeError(
                    _("{m} takes at most {max} arguments ({n} given).").format(
                        m="index()", max=3, n=len(args) + 1
                    )
                )
            i = int(args[0])
            if len(args) > 1:
                j = int(args[1])

        index = 0
        start = 0
        if i is not None:
            start = i
            if i < 0:
                start = len(self._list) + i

        wrap = False
        end = len(self._list)
        if j is not None:
            if j < 0:
                end = len(self._list) + j
                if end < index:
                    wrap = True
            else:
                end = j
        for index in list(range(len(self._list))):
            item = self._list[index]
            if index < start:
                continue
            if index >= end and not wrap:
                break
            if item == group:
                return index

        if wrap:
            for index in list(range(len(self._list))):
                item = self._list[index]
                if index >= end:
                    break
            if item == group:
                return index

        msg = _("group is not in group list.")
        raise ValueError(msg)

    # -------------------------------------------------------------------------
    def __contains__(self, group):
        """Return whether the given port group is contained in current list."""
        if not isinstance(group, VsphereHostPortgroup):
            raise TypeError(
                self.msg_no_portgroup.format(
                    t=group.__class__.__name__, c=self.__class__.__name__, o="VsphereHostPortgroup"
                )
            )

        if not self._list:
            return False

        for item in self._list:
            if item == group:
                return True

        return False

    # -------------------------------------------------------------------------
    def count(self, group):
        """Return the number of port groups which are equal to the given one in current list."""
        if not isinstance(group, VsphereHostPortgroup):
            raise TypeError(
                self.msg_no_portgroup.format(
                    t=group.__class__.__name__, c=self.__class__.__name__, o="VsphereHostPortgroup"
                )
            )

        if not self._list:
            return 0

        num = 0
        for item in self._list:
            if item == group:
                num += 1
        return num

    # -------------------------------------------------------------------------
    def __len__(self):
        """Return the number of port groups in current list."""
        return len(self._list)

    # -------------------------------------------------------------------------
    def __getitem__(self, key):
        """Get a port group from current list by the given numeric index."""
        return self._list.__getitem__(key)

    # -------------------------------------------------------------------------
    def __reversed__(self):
        """Reverse the port groups in list in place."""
        new_list = self.__class__(
            appname=self.appname, verbose=self.verbose, base_dir=self.base_dir, initialized=False
        )

        for group in reversed(self._list):
            new_list.append(copy.copy(group))

        new_list.initialized = self.initialized
        return new_list

    # -------------------------------------------------------------------------
    def __setitem__(self, key, group):
        """Replace the port group at the given numeric index by the given one."""
        if not isinstance(group, VsphereHostPortgroup):
            raise TypeError(
                self.msg_no_portgroup.format(
                    t=group.__class__.__name__, c=self.__class__.__name__, o="VsphereHostPortgroup"
                )
            )

        self._list.__setitem__(key, group)

    # -------------------------------------------------------------------------
    def __delitem__(self, key):
        """Remove the port group at the given numeric index from list."""
        del self._list[key]

    # -------------------------------------------------------------------------
    def append(self, group):
        """Append the given port group to the current list."""
        if not isinstance(group, VsphereHostPortgroup):
            raise TypeError(
                self.msg_no_portgroup.format(
                    t=group.__class__.__name__, c=self.__class__.__name__, o="VsphereHostPortgroup"
                )
            )

        self._list.append(group)

    # -------------------------------------------------------------------------
    def insert(self, index, group):
        """Insert the given port group in current list at given index."""
        if not isinstance(group, VsphereHostPortgroup):
            raise TypeError(
                self.msg_no_portgroup.format(
                    t=group.__class__.__name__, c=self.__class__.__name__, o="VsphereHostPortgroup"
                )
            )

        self._list.insert(index, group)

    # -------------------------------------------------------------------------
    def clear(self):
        """Remove all items from the VsphereHostPortgroupList."""
        self._list = []

    # -------------------------------------------------------------------------
    def ordered(self):
        """Iterate through the port groups in sorted order."""
        try:
            for group in sorted(self._list, key=lambda x: x.name.lower()):
                yield group
        except StopIteration:
            pass


# =============================================================================
if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
