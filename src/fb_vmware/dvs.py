#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for a vSphere Distributed Virtual Switching.

          The following classes were definded:
          * Distributed Virtual Switch
          * Distributed Virtual Port Group

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import absolute_import

# Standard modules
import logging

# Third party modules
from fb_tools.common import pp, to_bool

from pyVmomi import vim

# Own modules
from .errors import VSphereHandlerError
from .errors import VSphereNameError
from .network import VsphereNetwork
from .obj import DEFAULT_OBJ_STATUS
from .obj import VsphereObject
from .xlate import XLATOR

__version__ = "1.0.1"
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext


# =============================================================================
class VsphereDVS(VsphereObject):
    """Wrapper class for a vSphere Distributed Virtual Switch (vim.DistributedVirtualSwitch)."""

    properties = [
        "contact_info",
        "contact_name",
        "create_time",
        "dc_name",
        "def_proxy_switch_max_num_ports",
        "description",
        "extension_key",
        "ip_address",
        "max_ports",
        "net_resource_mgmt_enabled",
        "num_hosts",
        "num_ports",
        "num_standalone_ports",
        "pnic_cap_ratio_reservation",
        "product_name",
        "product_vendor",
        "product_version",
        "uuid",
        "vsphere",
    ]

    prop_source = {
        "uuid": "uuid",
    }

    prop_source_config = {
        "create_time": "createTime",
        "def_proxy_switch_max_num_ports": "defaultProxySwitchMaxNumPorts",
        "description": "description",
        "extension_key": "extensionKey",
        "ip_address": "switchIpAddress",
        "max_ports": "maxPorts",
        "name": "name",
        "net_resource_mgmt_enabled": "networkResourceManagementEnabled",
        "num_ports": "numPorts",
        "num_standalone_ports": "numStandalonePorts",
        "pnic_cap_ratio_reservation": "pnicCapacityRatioForReservation",
    }

    prop_source_contact = {
        "contact_info": "contact",
        "contact_name": "name",
    }

    prop_source_product = {
        "product_name": "name",
        "product_vendor": "vendor",
        "product_version": "version",
    }

    prop_source_summary = {
        "num_hosts": "numHosts",
    }

    necessary_fields = [
        "uuid",
    ]

    necessary_config_fields = [
        "createTime",
        "maxPorts",
        "numPorts",
        "numStandalonePorts",
    ]

    repr_fields = ["name"] + properties + ["appname", "verbose"]

    # -------------------------------------------------------------------------
    def __init__(
        self,
        appname=None,
        verbose=0,
        version=__version__,
        base_dir=None,
        initialized=None,
        name=None,
        obj_type="vsphere_vds",
        name_prefix="vds",
        status=DEFAULT_OBJ_STATUS,
        config_status=DEFAULT_OBJ_STATUS,
        **kwargs,
    ):
        """Initialize a VsphereDVS object."""
        for prop in self.properties:
            setattr(self, "_" + prop, None)

        self._dvs = None

        super(VsphereDVS, self).__init__(
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
            if argname not in self.properties:
                msg = _("Invalid Argument {arg!r} on {what} given.").format(
                    arg=argname, what="VsphereDVS.init()"
                )
                raise AttributeError(msg)
            if kwargs[argname] is not None:
                setattr(self, "_" + argname, kwargs[argname])

        if initialized is not None:
            self.initialized = initialized

        if self.verbose > 3:
            LOG.debug(_("Initialized Distributed Virtual Switch:") + "\n" + pp(self.as_dict()))

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
    def dc_name(self):
        """Return the datacenter name of the VDS."""
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

    # -----------------------------------------------------------
    @property
    def vsphere(self):
        """Return the name of the vSphere of the VDS."""
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
            LOG.debug(_("Comparing {} objects ...").format(self.__class__.__name__))

        if not isinstance(other, VsphereDVS):
            return False

        if self.vsphere != other.vsphere:
            return False

        if self.dc_name != other.dc_name:
            return False

        if self.uuid != other.uuid:
            return False

        return True

    # -------------------------------------------------------------------------
    def search_port_keys(self, portgroup_key):
        """Search usable ports in the current DVS by a Port Group key."""
        if not self._dvs:
            msg = _("No {o} reference found in VDS {n!r}.").format(
                o="vim.DistributedVirtualSwitch", n=self.name
            )
            raise RuntimeError(msg)

        port_keys = []
        criteria = vim.dvs.PortCriteria()
        criteria.connected = False
        criteria.inside = True
        criteria.portgroupKey = portgroup_key

        ports = self._dvs.FetchDVPorts(criteria)
        for port in ports:
            port_keys.append(port.key)
        if self.verbose > 1:
            msg = _("Found usable port keys for DVS {!r}:").format(self.name)
            msg += " " + pp(port_keys)

        return port_keys

    # -------------------------------------------------------------------------
    def find_port_by_portkey(self, port_key):
        """Find a port object by a given port key."""
        if not self._dvs:
            msg = _("No {o} reference found in VDS {n!r}.").format(
                o="vim.DistributedVirtualSwitch", n=self.name
            )
            raise RuntimeError(msg)

        obj = None
        ports = self._dvs.FetchDVPorts()
        for port in ports:
            if port.key == port_key:
                obj = port

        return obj

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
        """Create a new VsphereDVS object based on the data given from pyvmomi."""
        params = {
            "vsphere": vsphere,
            "dc_name": dc_name,
            "appname": appname,
            "verbose": verbose,
            "base_dir": base_dir,
            "initialized": True,
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
                LOG.debug(_("Creating {} object from:").format(cls.__name__) + "\n" + pp(params))
            else:
                LOG.debug(
                    _("Creating {cls} object {name!r}.").format(
                        cls=cls.__name__, name=data.summary.name
                    )
                )

        vds = cls(**params)

        vds._dvs = data

        return vds


# =============================================================================
class VsphereDvPortGroup(VsphereNetwork):
    """Wrapper class for a Network definition in vSphere (vim.dvs.DistributedVirtualPortgroup)."""

    dvpg_properties = [
        "auto_expand",
        "backing_type",
        "description",
        "dvs_uuid",
        "key",
        "num_ports",
        "port_keys",
        "port_name_format",
        "segment_id",
        "subnet_id",
        "vlan_id",
        "pg_type",
        "uplink",
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
        "auto_expand",
        "backing_type",
        "description",
        "dvs_uuid",
        "key",
        "num_ports",
        "port_keys",
        "port_name_format",
        "segment_id",
        "subnet_id",
        "pg_type",
        "uplink",
    ]

    dvpg_prop_source = {
        "key": "key",
        "port_keys": "portKeys",
    }

    dvpg_prop_source_config = {
        "auto_expand": "autoExpand",
        "backing_type": "backingType",
        "description": "description",
        "num_ports": "numPorts",
        "port_name_format": "portNameFormat",
        "segment_id": "segmentId",
        "subnet_id": "subnetId",
        "pg_type": "type",
        "uplink": "uplink",
    }

    obj_desc_singular = _("Distrubuted Virtual Port Group")
    obj_desc_plural = _("Distrubuted Virtual Port Groups")

    # -------------------------------------------------------------------------
    def __init__(
        self,
        appname=None,
        verbose=0,
        version=__version__,
        base_dir=None,
        initialized=None,
        name=None,
        obj_type="vsphere_dvportgroup",
        name_prefix="dvpg",
        status=DEFAULT_OBJ_STATUS,
        config_status=DEFAULT_OBJ_STATUS,
        **kwargs,
    ):
        """Initialize a VsphereDvPortGroup object."""
        for prop in self.dvpg_properties:
            setattr(self, "_" + prop, None)

        init_args = {
            "name": name,
            "obj_type": obj_type,
            "name_prefix": name_prefix,
            "status": status,
            "config_status": config_status,
            "appname": appname,
            "verbose": verbose,
            "version": version,
            "base_dir": base_dir,
            "initialized": initialized,
        }

        for arg in kwargs:
            if arg in self.net_properties:
                init_args[arg] = kwargs[arg]

        super(VsphereDvPortGroup, self).__init__(**init_args)

        self.initialized = False

        for arg in kwargs:
            if arg not in self.net_properties and arg not in self.dvpg_properties:
                msg = _("Invalid Argument {arg!r} on {what} given.").format(
                    arg=arg, what="VsphereNetwork.init()"
                )
                raise AttributeError(msg)
            if arg in self.dvpg_properties and kwargs[arg] is not None:
                setattr(self, arg, kwargs[arg])

        if initialized is not None:
            self.initialized = initialized

        if self.verbose > 3:
            LOG.debug(_("Initialized network object:") + "\n" + pp(self.as_dict()))

    # -----------------------------------------------------------
    @property
    def auto_expand(self):
        """Return, whether the number of ports will be ignored."""
        return self._auto_expand

    @auto_expand.setter
    def auto_expand(self, value):
        if value is None:
            self._auto_expand = None
            return
        self._auto_expand = to_bool(value)

    # -----------------------------------------------------------
    @property
    def backing_type(self):
        """Return the backing type of the portgroup."""
        return self._backing_type

    @backing_type.setter
    def backing_type(self, value):
        self._backing_type = value

    # -----------------------------------------------------------
    @property
    def description(self):
        """Return the description of the portgroup."""
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    # -----------------------------------------------------------
    @property
    def dvs_uuid(self):
        """Return the UUID of the Distributed virtual Switch of the portgroup."""
        return self._dvs_uuid

    @dvs_uuid.setter
    def dvs_uuid(self, value):
        self._dvs_uuid = value

    # -----------------------------------------------------------
    @property
    def key(self):
        """Return the generated UUID of the portgroup."""
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    # -----------------------------------------------------------
    @property
    def num_ports(self):
        """Return the number of ports in the portgroup."""
        return self._num_ports

    @num_ports.setter
    def num_ports(self, value):
        if value is None:
            self._num_ports = None
            return
        self._num_ports = int(value)

    # -----------------------------------------------------------
    @property
    def port_keys(self):
        """Return the port keys for the set of ports in the portgroup.."""
        return self._port_keys

    @port_keys.setter
    def port_keys(self, value):
        self._port_keys = value

    # -----------------------------------------------------------
    @property
    def port_name_format(self):
        """Return the port name format of the portgroup."""
        return self._port_name_format

    @port_name_format.setter
    def port_name_format(self, value):
        self._description = value

    # -----------------------------------------------------------
    @property
    def subnet_id(self):
        """Return the subnet ID of the portgroup."""
        return self._subnet_id

    @subnet_id.setter
    def subnet_id(self, value):
        self._subnet_id = value

    # -----------------------------------------------------------
    @property
    def segment_id(self):
        """Return the segment ID of the portgroup."""
        return self._segment_id

    @segment_id.setter
    def segment_id(self, value):
        self._segment_id = value

    # -----------------------------------------------------------
    @property
    def vlan_id(self):
        """Return the VLAN ID of the portgroup."""
        return self._vlan_id

    @vlan_id.setter
    def vlan_id(self, value):
        self._vlan_id = value

    # -----------------------------------------------------------
    @property
    def pg_type(self):
        """Return the type of the portgroup."""
        return self._pg_type

    @pg_type.setter
    def pg_type(self, value):
        self._pg_type = value

    # -----------------------------------------------------------
    @property
    def uplink(self):
        """Return, whether the portgroup is an uplink portgroup."""
        return self._uplink

    @uplink.setter
    def uplink(self, value):
        if value is None:
            self._uplink = None
            return
        self._uplink = to_bool(value)

    # -----------------------------------------------------------
    def get_pyvmomi_obj(self, service_instance):
        """Return the appropriate PyVMomi object for the current object."""
        obj = None
        if not self.name:
            return None

        content = service_instance.RetrieveContent()
        container = content.viewManager.CreateContainerView(
            content.rootFolder, vim.dvs.DistributedVirtualPortgroup, True)
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
        res = super(VsphereDvPortGroup, self).as_dict(short=short)

        for prop in self.dvpg_properties:
            res[prop] = getattr(self, prop)

        return res

    # -------------------------------------------------------------------------
    @classmethod
    def get_init_params(cls, data, verbose=0):
        """Return a dict with all keys for init a new network object with from_summary()."""
        params = super(VsphereDvPortGroup, cls).get_init_params(data, verbose=verbose)

        for prop in cls.dvpg_prop_source:
            prop_src = cls.dvpg_prop_source[prop]
            value = getattr(data, prop_src, None)
            if value is not None:
                params[prop] = value

        for prop in cls.dvpg_prop_source_config:
            prop_src = cls.dvpg_prop_source_config[prop]
            value = getattr(data.config, prop_src, None)
            if value is not None:
                params[prop] = value

        if hasattr(data.config, "distributedVirtualSwitch"):
            params["dvs_uuid"] = data.config.distributedVirtualSwitch.uuid

        if hasattr(data.config, "defaultPortConfig"):
            if hasattr(data.config.defaultPortConfig, "vlan"):
                vlan_info = data.config.defaultPortConfig.vlan
                vlan_spec = vim.dvs.VmwareDistributedVirtualSwitch.TrunkVlanSpec
                if isinstance(vlan_info, vlan_spec):
                    vlanlist = []
                    for item in vlan_info.vlanId:
                        if item.start == item.end:
                            vlanlist.append(str(item.start))
                        else:
                            vlanlist.append(str(item.start) + "-" + str(item.end))
                    params["vlan_id"] = ",".join(vlanlist)
                else:
                    params["vlan_id"] = str(vlan_info.vlanId)

        return params

    # -------------------------------------------------------------------------
    def get_params_dict(self):
        """Return a dict with all keys for init a new network object with __init__."""
        params = super(VsphereDvPortGroup, self).get_params_dict()

        for prop in self.dvpg_properties:
            val = getattr(self, prop, None)
            params[prop] = val

        return params

    # -------------------------------------------------------------------------
    def get_if_backing_device(self, port):
        """Return a backing device for a new virtual network interface."""
        if self.verbose > 1:
            msg = _(
                "Creating network device backing specification with a "
                "Distributed Virtual Port Group."
            )
            LOG.debug(msg)

        backing_device = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()

        backing_device.port = vim.dvs.PortConnection()
        backing_device.port.portgroupKey = port.portgroupKey
        backing_device.port.switchUuid = port.dvsUuid
        backing_device.port.portKey = port.key

        if self.verbose > 0:
            msg = _("Got Backing device for port group {!r}:").format(self.name)
            LOG.debug(msg + " " + pp(backing_device))

        return backing_device


# =============================================================================
if __name__ == "__main__":

    pass

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
