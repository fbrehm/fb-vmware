#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for a vSphere network object.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import absolute_import

# Standard modules
import copy
import ipaddress
import logging
import re

# Third party modules
from fb_tools.common import pp, to_bool
from fb_tools.obj import FbGenericBaseObject
from fb_tools.xlate import format_list

from pyVmomi import vim

# Own modules
from .errors import VSphereHandlerError
from .errors import VSphereNameError
from .errors import VSphereNoNetFoundError
from .obj import DEFAULT_OBJ_STATUS
from .obj import VsphereObject
from .typed_dict import TypedDict
from .xlate import XLATOR

__version__ = "1.10.3"
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext
ngettext = XLATOR.ngettext


# =============================================================================
class VsphereNetwork(VsphereObject):
    """Wrapper class for a Network definition in vSphere (vim.Network)."""

    re_ipv4_name = re.compile(r"\s*((?:\d{1,3}\.){3}\d{1,3})_(\d+)\s*$")
    re_tf_name = re.compile(r"[^a-z0-9_]+", re.IGNORECASE)

    net_properties = [
        "accessible",
        "dc_name",
        "ip_pool_id",
        "ip_pool_name",
        "vsphere",
    ]

    repr_fields = [
        "name",
        "obj_type",
        "vsphere",
        "dc_name",
        "status",
        "config_status",
        "accessible",
        "ip_pool_id",
        "ip_pool_name",
        "appname",
        "verbose",
    ]

    net_prop_source = {
        "status": "overallStatus",
        "config_status": "configStatus",
    }

    net_prop_source_summary = {
        "name": "name",
        "accessible": "accessible",
        "ip_pool_id": "ipPoolId",
        "ip_pool_name": "ipPoolName",
    }

    obj_desc_singular = _("Virtual Network")
    obj_desc_plural = _("Virtual Networks")

    necessary_net_fields = ["summary", "overallStatus", "configStatus"]
    necessary_net_summary_fields = ["name"]

    warn_unassigned_net = True

    # -------------------------------------------------------------------------
    def __init__(
        self,
        appname=None,
        verbose=0,
        version=__version__,
        base_dir=None,
        initialized=None,
        name=None,
        obj_type="vsphere_network",
        name_prefix="net",
        status=DEFAULT_OBJ_STATUS,
        config_status=DEFAULT_OBJ_STATUS,
        **kwargs,
    ):
        """Initialize a VsphereNetwork object."""
        for prop in self.net_properties:
            setattr(self, "_" + prop, None)

        self._network = None

        super(VsphereNetwork, self).__init__(
            name=name,
            obj_type=obj_type,
            name_prefix=name_prefix,
            status=status,
            config_status=config_status,
            appname=appname,
            verbose=verbose,
            version=version,
            base_dir=base_dir,
        )

        for argname in kwargs:
            if argname not in self.net_properties:
                msg = _("Invalid Argument {arg!r} on {what} given.").format(
                    arg=argname, what="VsphereNetwork.init()"
                )
                raise AttributeError(msg)
            if kwargs[argname] is not None:
                setattr(self, argname, kwargs[argname])

        match = self.re_ipv4_name.search(self.name)
        if match:
            ip = "{a}/{m}".format(a=match.group(1), m=match.group(2))
            if self.verbose > 3:
                LOG.debug(
                    _("Trying to get IPv4 network {n!r} -> {i!r}.").format(n=self.name, i=ip)
                )

            try:
                net = ipaddress.ip_network(ip)
                self._network = net
            except ValueError:
                LOG.error(_("Could not get IP network from network name {!r}.").format(self.name))

        if not self.network:
            msg = _("Network {!r} has no IP network assigned.").format(self.name)
            if self.warn_unassigned_net:
                LOG.warning(msg)
            else:
                LOG.debug(msg)

        if initialized is not None:
            self.initialized = initialized

        if self.verbose > 4:
            LOG.debug(_("Initialized network object:") + "\n" + pp(self.as_dict()))

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
    def dc_name(self):
        """Return the datacenter name of the network."""
        return self._dc_name

    @dc_name.setter
    def dc_name(self, value):

        if value is None:
            self._dc_name = None
            return

        val = str(value)
        if val == "":
            raise VSphereNameError(value, self.obj_type)

        self._dc_name = val

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

    # -----------------------------------------------------------
    @property
    def vsphere(self):
        """Return the name of the vSphere of the network."""
        return self._vsphere

    @vsphere.setter
    def vsphere(self, value):
        if value is None:
            self._vsphere = None
            return

        val = str(value).strip()
        if val == "":
            msg = _("The name of the vSphere may not be empty.")
            raise VSphereHandlerError(msg)

        self._vsphere = val

    # -----------------------------------------------------------
    def get_pyvmomi_obj(self, service_instance):
        """Return the appropriate PyVMomi object for the current object."""
        obj = None
        if not self.name:
            return None

        content = service_instance.RetrieveContent()
        container = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.Network], True
        )
        for c in container.view:
            if c.name == self.name:
                obj = c
                break

        return obj

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

        res["network"] = self.network
        res["gateway"] = self.gateway

        return res

    # -------------------------------------------------------------------------
    @classmethod
    def from_summary(
        cls,
        data,
        vsphere=None,
        dc_name=None,
        appname=None,
        verbose=0,
        base_dir=None,
        test_mode=False,
    ):
        """Create a new VsphereNetwork object based on the data given from pyvmomi."""
        if test_mode:

            failing_fields = []

            for field in cls.necessary_net_fields:
                if not hasattr(data, field):
                    failing_fields.append(field)

            if hasattr(data, "summary"):
                for field in cls.necessary_net_summary_fields:
                    if not hasattr(data.summary, field):
                        failing_fields.append("summary." + field)

            if len(failing_fields):
                msg = _(
                    "The given parameter {p!r} on calling method {m}() has failing " "attributes"
                ).format(p="data", m="from_summary")
                msg += ": " + format_list(failing_fields, do_repr=True)
                raise AssertionError(msg)

        else:
            if not isinstance(data, vim.Network):
                msg = _("Parameter {t!r} must be a {e}, {v!r} was given.").format(
                    t="data", e="vim.Network", v=data
                )
                raise TypeError(msg)

        common_params = {
            "vsphere": vsphere,
            "dc_name": dc_name,
            "appname": appname,
            "verbose": verbose,
            "base_dir": base_dir,
            "initialized": True,
        }
        params = cls.get_init_params(data=data, verbose=verbose)
        params.update(common_params)

        if verbose > 1:
            if verbose > 3:
                LOG.debug(_("Creating {} object from:").format(cls.__name__) + "\n" + pp(params))
            else:
                LOG.debug(
                    _("Creating {cls} object {name!r}.").format(
                        cls=cls.__name__, name=data.summary.name
                    )
                )

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
            "appname": self.appname,
            "verbose": self.verbose,
            "base_dir": self.base_dir,
            "initialized": self.initialized,
            "name": self.name,
            "obj_type": self.obj_type,
            "name_prefix": self.name_prefix,
            "status": self.status,
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
            LOG.debug(_("Comparing {} objects ...").format(self.__class__.__name__))

        if not isinstance(other, VsphereNetwork):
            return False

        if self.__class__.__name__ != other.__class__.__name__:
            return False

        if self.name != other.name:
            return False

        return True

    # -------------------------------------------------------------------------
    def get_if_backing_device(self, port=None):
        """Return a backing device for a new virtual network interface."""
        if self.verbose > 1:
            msg = _("Creating network device backing spcification with a Virtual Network.")
            LOG.debug(msg)

        backing_device = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()

        backing_device.useAutoDetect = False
        backing_device.deviceName = self.name

        if self.verbose > 0:
            msg = _("Got Backing device for network {!r}:").format(self.name)
            LOG.debug(msg + " " + pp(backing_device))

        return backing_device


# =============================================================================
class VsphereNetworkDict(TypedDict):
    """A dictionary containing VsphereNetwork objects."""

    value_class = VsphereNetwork

    msg_invalid_net_type = _("Invalid item type {{!r}} to set, only {} allowed.").format(
        "VsphereNetwork"
    )
    msg_key_not_name = _("The key {k!r} must be equal to the network name {n!r}.")

    # -------------------------------------------------------------------------
    def check_key_by_item(self, key, item):
        """Check the key by the given item."""
        if not isinstance(item, VsphereNetwork):
            raise TypeError(self.msg_invalid_net_type.format(item.__class__.__name__))

        net_name = item.name
        if net_name != key:
            raise KeyError(self.msg_key_not_name.format(k=key, n=net_name))

        return True

    # -------------------------------------------------------------------------
    def get_key_from_item(self, item):
        """Return the network name as a key from the item."""
        if not isinstance(item, VsphereNetwork):
            raise TypeError(self.msg_invalid_net_type.format(item.__class__.__name__))

        return item.name

    # -------------------------------------------------------------------------
    def compare(self, x, y):
        """Compare two items, used with functools for sorting. Maybe overridden."""
        net_x = self[x]
        net_y = self[y]

        if net_x.network is None and net_y.network is None:
            if net_x.name.lower() > net_y.name.lower():
                return -1
            if net_x.name.lower() > net_y.name.lower():
                return 1
            return 0

        if net_x.network is None:
            return -1

        if net_y.network is None:
            return 1

        if net_x.network < net_y.network:
            return -1

        if net_x.network > net_y.network:
            return 1

        return 0

    # -------------------------------------------------------------------------
    def get_network_for_ip(self, *ips):
        """
        Search a fitting network for the give IP addresses.

        The name of the first matching network for the first IP address, which will
        have a match, will be returned.
        """
        if len(self) < 1:
            LOG.debug(_("Empty {what}.").format(what=self.__class__.__name__))
            return None

        ips_list_str = []

        for ip in ips:
            if not ip:
                continue
            ips_list_str.append(str(ip))
            LOG.debug(_("Searching vSphere network for address {} ...").format(ip))
            ipa = ipaddress.ip_address(ip)

            for net_name in self.keys():
                net = self[net_name]
                if net.network and ipa in net.network:
                    desc = net.obj_desc_singular
                    LOG.debug(_("Found {d} {n!r} for IP {i}.").format(d=desc, n=net_name, i=ip))
                    return net_name

            desc = self.value_class.obj_desc_singular
            LOG.debug(_("Could not find {d} for IP {ip}.").format(d=desc, ip=ip))

        ips_str = format_list(ips_list_str)
        no_ips = len(ips_list_str)

        msg = ngettext(
            "Could not find {d} for IP address {ips}.",
            "Could not find {d} for IP addresses {ips}.",
            no_ips,
        ).format(d=self.value_class.obj_desc_singular, ips=ips_str)
        raise VSphereNoNetFoundError(msg)


# =============================================================================
class GeneralNetworksDict(dict, FbGenericBaseObject):
    """Encapsulate Network lists of multiple vSphere instances."""

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """Transform the values of the dict into dicts."""
        res = {}
        for key in self:
            item = self[key]
            if isinstance(item, FbGenericBaseObject):
                res[key] = self[key].as_dict(short)
            else:
                res[key] = copy.copy(self[key].__dict__)

        return res

    # -------------------------------------------------------------------------
    def as_lists(self, short=True):
        """Transform the values of the dict into lists of items."""
        res = {}
        for key in self:
            item = self[key]
            res[key] = []
            if hasattr(item, "as_list"):
                res[key] = self[key].as_list(short)
            elif hasattr(item, "values"):
                for value in self[key].values():
                    res[key].append(value)
            else:
                res[key].append(item)

        return res


# =============================================================================
if __name__ == "__main__":

    pass

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
