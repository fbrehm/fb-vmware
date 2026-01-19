#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for capsulating a vSphere host system object.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import absolute_import

# Standard modules
import copy
import datetime
import ipaddress
import logging
import uuid

try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence

# Third party modules
from fb_tools.common import pp, to_bool
from fb_tools.obj import FbBaseObject
from fb_tools.xlate import format_list

from pyVmomi import vim

# Own modules
from .about import VsphereAboutInfo
from .errors import VSphereHandlerError
from .errors import VSphereNameError
from .host_port_group import VsphereHostPortgroup, VsphereHostPortgroupList
from .obj import DEFAULT_OBJ_STATUS, OBJ_STATUS_GREEN
from .obj import VsphereObject
from .xlate import XLATOR

__version__ = "1.3.1"
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext


# =============================================================================
class VsphereHostBiosInfo(FbBaseObject):
    """Wrapper class for virtual BIOS informations."""

    # -------------------------------------------------------------------------
    def __init__(
        self,
        bios_version=None,
        fw_major=None,
        fw_minor=None,
        major=None,
        minor=None,
        release_date=None,
        vendor=None,
        appname=None,
        verbose=0,
        version=__version__,
        base_dir=None,
        initialized=None,
    ):
        """Initialize a VsphereHostBiosInfo object."""
        self._bios_version = None
        self._fw_major = None
        self._fw_minor = None
        self._major = None
        self._minor = None
        self._release_date = None
        self._vendor = None

        super(VsphereHostBiosInfo, self).__init__(
            appname=appname, verbose=verbose, version=version, base_dir=base_dir
        )

        self.bios_version = bios_version
        self.fw_major = fw_major
        self.fw_minor = fw_minor
        self.major = major
        self.minor = minor
        self.release_date = release_date
        self.vendor = vendor

        if initialized is not None:
            self.initialized = initialized

    # -----------------------------------------------------------
    @property
    def bios_version(self):
        """Return the BIOS name of the host."""
        return self._bios_version

    @bios_version.setter
    def bios_version(self, value):
        if value is None:
            self._bios_version = None
            return
        v = str(value).strip()
        if v == "":
            self._bios_version = None
        else:
            self._bios_version = v

    # -----------------------------------------------------------
    @property
    def fw_major(self):
        """Return the major version of the firmware of the BIOS of the host."""
        return self._fw_major

    @fw_major.setter
    def fw_major(self, value):
        if value is None:
            self._fw_major = None
            return
        v = str(value).strip()
        if v == "":
            self._fw_major = None
        else:
            self._fw_major = v

    # -----------------------------------------------------------
    @property
    def fw_minor(self):
        """Return the minor version of the firmware of the BIOS of the host."""
        return self._fw_minor

    @fw_minor.setter
    def fw_minor(self, value):
        if value is None:
            self._fw_minor = None
            return
        v = str(value).strip()
        if v == "":
            self._fw_minor = None
        else:
            self._fw_minor = v

    # -----------------------------------------------------------
    @property
    def major(self):
        """Return the major version of the BIOS of the host."""
        return self._major

    @major.setter
    def major(self, value):
        if value is None:
            self._major = None
            return
        v = str(value).strip()
        if v == "":
            self._major = None
        else:
            self._major = v

    # -----------------------------------------------------------
    @property
    def minor(self):
        """Return the minor version of the BIOS of the host."""
        return self._minor

    @minor.setter
    def minor(self, value):
        if value is None:
            self._minor = None
            return
        v = str(value).strip()
        if v == "":
            self._minor = None
        else:
            self._minor = v

    # -----------------------------------------------------------
    @property
    def release_date(self):
        """Return the release date of the BIOS of the host."""
        return self._release_date

    @release_date.setter
    def release_date(self, value):
        if value is None:
            self._release_date = None
            return
        if isinstance(value, (datetime.datetime, datetime.date)):
            self._release_date = value
            return
        v = str(value).strip()
        if v == "":
            self._release_date = None
        else:
            self._release_date = v

    # -----------------------------------------------------------
    @property
    def vendor(self):
        """Return the vendor of the BIOS of the host."""
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

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transform the elements of the object into a dict.

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """
        res = super(VsphereHostBiosInfo, self).as_dict(short=short)

        res["bios_version"] = self.bios_version
        res["fw_major"] = self.fw_major
        res["fw_minor"] = self.fw_minor
        res["major"] = self.major
        res["minor"] = self.minor
        res["release_date"] = self.release_date
        res["vendor"] = self.vendor

        return res

    # -------------------------------------------------------------------------
    def __copy__(self):
        """Return a new VsphereHostBiosInfo as a deep copy of the current object."""
        info = VsphereHostBiosInfo(
            appname=self.appname,
            verbose=self.verbose,
            base_dir=self.base_dir,
            initialized=self.initialized,
            bios_version=self.bios_version,
            fw_major=self.fw_major,
            fw_minor=self.fw_minor,
            major=self.major,
            minor=self.minor,
            release_date=self.release_date,
            vendor=self.vendor,
        )

        return info

    # -------------------------------------------------------------------------
    @classmethod
    def from_summary(cls, data, appname=None, verbose=0, base_dir=None, test_mode=False):
        """Create a new VsphereDiskController object based on the data given from pyvmomi."""
        if test_mode:

            necessary_fields = ("biosVersion", "releaseDate")

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
            if not isinstance(data, vim.host.BIOSInfo):
                msg = _("Parameter {t!r} must be a {e}, {v!r} ({vt}) was given.").format(
                    t="data", e="vim.host.BIOSInfo", v=data, vt=data.__class__.__name__
                )
                raise TypeError(msg)

        params = {
            "appname": appname,
            "verbose": verbose,
            "base_dir": base_dir,
            "initialized": True,
            "bios_version": data.biosVersion,
            "release_date": data.releaseDate,
        }
        if hasattr(data, "firmwareMajorRelease"):
            params["fw_major"] = data.firmwareMajorRelease
        if hasattr(data, "firmwareMinorRelease"):
            params["fw_minor"] = data.firmwareMinorRelease
        if hasattr(data, "majorRelease"):
            params["major"] = data.majorRelease
        if hasattr(data, "minorRelease"):
            params["minor"] = data.minorRelease
        if hasattr(data, "vendor"):
            params["vendor"] = data.vendor

        if verbose > 2:
            LOG.debug(_("Creating {} object from:").format(cls.__name__) + "\n" + pp(params))

        bios = cls(**params)

        return bios


# =============================================================================
class VsphereHost(VsphereObject):
    """Wrapper class for a vim.HostSystem, which is the represtation of a physical ESX host."""

    power_state_label = {
        "poweredOn": _("powered on"),
        "poweredOff": _("powered off"),
        "standBy": _("stand by"),
        "unknown": _("unknown"),
    }

    connect_state_label = {
        "connected": _("connected"),
        "notResponding": _("not responding"),
        "disconnected": _("disconnected"),
    }

    standby_mode_label = {
        "entering": _("entering"),
        "exiting": _("exiting"),
        "in": _("in"),
        "none": _("none"),
    }

    # -------------------------------------------------------------------------
    def __init__(
        self,
        appname=None,
        verbose=0,
        version=__version__,
        base_dir=None,
        initialized=None,
        name=None,
        dc_name=None,
        cluster_name=None,
        vsphere=None,
        status=DEFAULT_OBJ_STATUS,
        config_status=DEFAULT_OBJ_STATUS,
    ):
        """Initialize a VsphereHost object."""
        self.repr_fields = ("name", "dc_name", "vsphere")
        self._vsphere = None
        self._cluster_name = None
        self.bios = None
        self.cpu_speed = None
        self.cpu_cores = None
        self.cpu_pkgs = None
        self.cpu_threads = None
        self.memory = None
        self.model = None
        self.uuid = None
        self.vendor = None
        self._boot_time = None
        self._maintenance = False
        self._quarantaine = False
        self.connection_state = None
        self.power_state = None
        self.standby = None
        self._reboot_required = False
        self._mgmt_ip = None
        self.ipv6_enabled = None
        self.atboot_ipv6_enabled = None
        self.portgroups = None
        self._dc_name = None

        self.product = None

        super(VsphereHost, self).__init__(
            name=name,
            obj_type="vsphere_host",
            name_prefix="host",
            status=status,
            config_status=config_status,
            appname=appname,
            verbose=verbose,
            version=version,
            base_dir=base_dir,
        )

        self.dc_name = dc_name
        if vsphere is not None:
            self.vsphere = vsphere

        self.cluster_name = cluster_name

    # -----------------------------------------------------------
    @property
    def vsphere(self):
        """Return the name of the vSphere from configuration of the host."""
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
    @property
    def dc_name(self):
        """Return the datacenter name of the cluster."""
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
    def cluster_name(self):
        """Return the name of the compute resource, where this host is a member."""
        return self._cluster_name

    @cluster_name.setter
    def cluster_name(self, value):
        if value is None:
            self._cluster_name = None
            return
        v = str(value).strip().lower()
        if v == "":
            self._cluster_name = None
        else:
            self._cluster_name = v

    # -----------------------------------------------------------
    @property
    def mgmt_ip(self):
        """Return the management IP address of the host."""
        return self._mgmt_ip

    @mgmt_ip.setter
    def mgmt_ip(self, value):
        if value is None:
            self._mgmt_ip = None
            return
        v = str(value).strip().lower()
        if v == "":
            self._mgmt_ip = None
        else:
            try:
                v = ipaddress.ip_address(v)
            except Exception:
                pass
            self._mgmt_ip = v

    # -----------------------------------------------------------
    @property
    def memory_mb(self):
        """Return the RAM of the host in MiByte."""
        if self.memory is None:
            return None
        return int(self.memory / 1024 / 1024)

    # -----------------------------------------------------------
    @property
    def memory_gb(self):
        """Return the RAM of the host in GiByte."""
        if self.memory is None:
            return None
        return float(self.memory) / 1024.0 / 1024.0 / 1024.0

    # -----------------------------------------------------------
    @property
    def maintenance(self):
        """Is the host in maintenance mode."""
        return self._maintenance

    @maintenance.setter
    def maintenance(self, value):
        self._maintenance = to_bool(value)

    # -----------------------------------------------------------
    @property
    def quarantaine(self):
        """Is the host in quarantaine mode."""
        return self._quarantaine

    @quarantaine.setter
    def quarantaine(self, value):
        self._quarantaine = to_bool(value)

    # -----------------------------------------------------------
    @property
    def reboot_required(self):
        """Return, whether the host needs a reboot."""
        return self._reboot_required

    @reboot_required.setter
    def reboot_required(self, value):
        self._reboot_required = to_bool(value)

    # -----------------------------------------------------------
    @property
    def online(self):
        """Return, whether this host generally online or not."""
        if self.power_state is None:
            return False
        if self.power_state.lower() in ("poweredoff", "unknown"):
            return False
        return True

    # -----------------------------------------------------------
    @property
    def boot_time(self):
        """Return the time of the last reboot of the host."""
        return self._boot_time

    @boot_time.setter
    def boot_time(self, value):
        if value is None:
            self._boot_time = None
            return
        if isinstance(value, (datetime.datetime, datetime.date)):
            self._boot_time = value
            return
        v = str(value).strip()
        if v == "":
            self._boot_time = None
        else:
            self._boot_time = v

    # -----------------------------------------------------------
    def get_pyvmomi_obj(self, service_instance):
        """Return the appropriate PyVMomi object for the current object."""
        obj = None
        if not self.name:
            return None

        content = service_instance.RetrieveContent()
        container = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.HostSystem], True
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
        res = super(VsphereHost, self).as_dict(short=short)

        res["vsphere"] = self.vsphere
        res["dc_name"] = self.dc_name
        res["cluster_name"] = self.cluster_name
        res["memory_mb"] = self.memory_mb
        res["memory_gb"] = self.memory_gb
        res["boot_time"] = self.boot_time
        res["maintenance"] = self.maintenance
        res["quarantaine"] = self.quarantaine
        res["reboot_required"] = self.reboot_required
        res["mgmt_ip"] = self.mgmt_ip
        res["online"] = self.online
        res["portgroups"] = None
        if self.portgroups:
            res["portgroups"] = self.portgroups.as_dict(short=short)
        if self.bios is not None:
            res["bios"] = self.bios.as_dict(short=short)

        return res

    # -------------------------------------------------------------------------
    def __repr__(self):
        """Typecast into a string for reproduction."""
        out = "<%s(" % (self.__class__.__name__)

        fields = []
        fields.append("appname={!r}".format(self.appname))
        fields.append("verbose={!r}".format(self.verbose))
        fields.append("name={!r}".format(self.name))
        fields.append("dc_name={!r}".format(self.dc_name))
        fields.append("cluster_name={!r}".format(self.cluster_name))
        fields.append("initialized={!r}".format(self.initialized))

        out += ", ".join(fields) + ")>"
        return out

    # -------------------------------------------------------------------------
    def __copy__(self):
        """Return a new VsphereHost as a deep copy of the current object."""
        host = VsphereHost(
            appname=self.appname,
            verbose=self.verbose,
            base_dir=self.base_dir,
            initialized=self.initialized,
            vsphere=self.vsphere,
            name=self.name,
            dc_name=self.dc_name,
            status=self.status,
            config_status=self.config_status,
            cluster_name=self.cluster_name,
        )

        if self.bios:
            host.bios = copy.copy(self.bios)
        host.cpu_speed = self.cpu_speed
        host.cpu_cores = self.cpu_cores
        host.cpu_pkgs = self.cpu_pkgs
        host.cpu_threads = self.cpu_threads
        host.memory = self.memory
        host.model = self.model
        host.uuid = self.uuid
        host.vendor = self.vendor
        host.boot_time = self.boot_time
        host.maintenance = self.maintenance
        host.quarantaine = self.quarantaine
        host.connection_state = self.connection_state
        host.power_state = self.power_state
        host.standby = self.standby
        host.reboot_required = self.reboot_required
        host.mgmt_ip = self.mgmt_ip
        host.product = copy.copy(self.product)
        host.portgroups = copy.copy(self.portgroups)

        return host

    # -------------------------------------------------------------------------
    def __eq__(self, other):
        """Magic method for using it as the '=='-operator."""
        if self.verbose > 4:
            LOG.debug(_("Comparing {} objects ...").format(self.__class__.__name__))

        if not isinstance(other, VsphereHost):
            return False

        if self.vsphere != other.vsphere:
            return False
        if self.dc_name != other.dc_name:
            return False
        if self.name != other.name:
            return False

        return True

    # -------------------------------------------------------------------------
    @classmethod
    def from_summary(
        cls,
        data,
        vsphere=None,
        appname=None,
        verbose=0,
        base_dir=None,
        dc_name=None,
        cluster_name=None,
        test_mode=False,
    ):
        """Create a new VsphereHost object based on the data given from pyvmomi."""
        if test_mode:
            cls._check_summary_data(data)
        else:
            if not isinstance(data, vim.HostSystem):
                msg = _("Parameter {t!r} must be a {e}, {v!r} ({vt}) was given.").format(
                    t="data", e="vim.HostSystem", v=data, vt=data.__class__.__name__
                )
                raise TypeError(msg)

        if not data.config:
            LOG.error(_("Host {!r} seems to be offline!").format(data.summary.config.name))

        params = {
            "vsphere": vsphere,
            "appname": appname,
            "verbose": verbose,
            "base_dir": base_dir,
            "initialized": True,
            "name": data.summary.config.name,
            "dc_name": dc_name,
            "cluster_name": cluster_name,
            "status": DEFAULT_OBJ_STATUS,
            "config_status": OBJ_STATUS_GREEN,
        }

        if verbose > 2:
            LOG.debug(_("Creating {} object from:").format(cls.__name__) + "\n" + pp(params))

        host = cls(**params)

        host.bios = VsphereHostBiosInfo.from_summary(
            data.hardware.biosInfo,
            appname=appname,
            verbose=verbose,
            base_dir=base_dir,
            test_mode=test_mode,
        )

        host.cpu_speed = data.hardware.cpuInfo.hz
        host.cpu_cores = data.hardware.cpuInfo.numCpuCores
        host.cpu_pkgs = data.hardware.cpuInfo.numCpuPackages
        host.cpu_threads = data.hardware.cpuInfo.numCpuThreads
        host.memory = data.hardware.memorySize

        host.model = data.hardware.systemInfo.model
        try:
            host.uuid = uuid.UUID(data.hardware.systemInfo.uuid)
        except Exception:
            host.uuid = data.hardware.systemInfo.uuid
        host.vendor = data.hardware.systemInfo.vendor

        host.boot_time = data.runtime.bootTime
        host.connection_state = data.runtime.connectionState
        host.power_state = data.runtime.powerState
        host.standby = data.runtime.standbyMode
        host.maintenance = data.runtime.inMaintenanceMode
        host.quarantaine = data.runtime.inQuarantineMode

        host.mgmt_ip = data.summary.managementServerIp
        host.reboot_required = data.summary.rebootRequired

        host.product = None
        if data.config:
            host.product = VsphereAboutInfo.from_summary(
                data.config.product,
                appname=appname,
                verbose=verbose,
                base_dir=base_dir,
                test_mode=test_mode,
            )
            if data.config.network:
                host.ipv6_enabled = data.config.network.ipV6Enabled
                host.atboot_ipv6_enabled = data.config.network.atBootIpV6Enabled
                host.portgroups = VsphereHostPortgroupList(
                    appname=appname, verbose=verbose, base_dir=base_dir, hostname=host.name
                )
                for pg_data in data.config.network.portgroup:
                    pgroup = VsphereHostPortgroup.from_summary(
                        pg_data,
                        hostname=host.name,
                        appname=appname,
                        verbose=verbose,
                        base_dir=base_dir,
                        test_mode=test_mode,
                    )
                    host.portgroups.append(pgroup)

        return host

    # -------------------------------------------------------------------------
    @classmethod
    def _check_summary_data(cls, data):

        necessary_fields = ("summary", "hardware", "runtime", "config")
        runtime_fields = (
            "bootTime",
            "connectionState",
            "powerState",
            "standbyMode",
            "inMaintenanceMode",
            "inQuarantineMode",
        )
        summary_fields = ("managementServerIp", "rebootRequired")

        failing_fields = []

        for field in necessary_fields:
            if not hasattr(data, field):
                failing_fields.append(field)

        if hasattr(data, "hardware"):
            failing_fields += cls._check_hardware_data(data.hardware)

        if hasattr(data, "runtime"):
            for field in runtime_fields:
                if not hasattr(data.runtime, field):
                    failing_fields.append("runtime." + field)

        if hasattr(data, "summary"):
            for field in summary_fields:
                if not hasattr(data.summary, field):
                    failing_fields.append("summary." + field)

        if hasattr(data, "config") and data.config:
            failing_fields += cls._check_config_data(data.config)

        if len(failing_fields):
            msg = _(
                "The given parameter {p!r} on calling method {m}() has failing " "attributes"
            ).format(p="data", m="from_summary")
            msg += ": " + format_list(failing_fields, do_repr=True)
            raise AssertionError(msg)

    # -------------------------------------------------------------------------
    @classmethod
    def _check_hardware_data(cls, hardware):

        hardware_fields = ("biosInfo", "cpuInfo", "memorySize", "systemInfo")
        cpu_fields = ("hz", "numCpuCores", "numCpuPackages", "numCpuThreads")
        failing_fields = []

        for field in hardware_fields:
            if not hasattr(hardware, field):
                failing_fields.append("hardware." + field)

        if hasattr(hardware, "cpuInfo"):
            for field in cpu_fields:
                if not hasattr(hardware.cpuInfo, field):
                    failing_fields.append("hardware.cpuInfo." + field)

        if hasattr(hardware, "systemInfo"):
            if not hasattr(hardware.systemInfo, "model"):
                failing_fields.append("hardware.systemInfo.model")
            if not hasattr(hardware.systemInfo, "vendor"):
                failing_fields.append("hardware.systemInfo.vendor")

        return failing_fields

    # -------------------------------------------------------------------------
    @classmethod
    def _check_config_data(cls, config):

        failing_fields = []

        if not hasattr(config, "product"):
            failing_fields.append("config.product")
        if not hasattr(config, "network"):
            failing_fields.append("config.network")
        elif config.network:
            for field in ("ipV6Enabled", "atBootIpV6Enabled", "portgroup"):
                if not hasattr(config.network, field):
                    failing_fields.append("config.network." + field)

        return failing_fields


# =============================================================================
class VsphereHostList(FbBaseObject, MutableSequence):
    """A list containing VsphereHost objects."""

    msg_no_host = _(
        "Invalid type {{t!r}} as an item of a {{c}}, only {} objects are allowed."
    ).format("VsphereHost")

    # -------------------------------------------------------------------------
    def __init__(
        self, appname=None, verbose=0, version=__version__, base_dir=None, initialized=None, *hosts
    ):
        """Initialize a VsphereHostList object."""
        self._list = []

        super(VsphereHostList, self).__init__(
            appname=appname, verbose=verbose, version=version, base_dir=base_dir, initialized=False
        )

        for host in hosts:
            self.append(host)

        if initialized is not None:
            self.initialized = initialized

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
            for host in self:
                res.append(host.as_dict(short=True))
            return res

        res = super(VsphereHostList, self).as_dict(short=short)
        res["_list"] = []

        for host in self:
            res["_list"].append(host.as_dict(short=short))

        return res

    # -------------------------------------------------------------------------
    def __copy__(self):
        """Return a new VsphereHostList as a deep copy of the current object."""
        new_list = self.__class__(
            appname=self.appname, verbose=self.verbose, base_dir=self.base_dir, initialized=False
        )

        for host in self:
            new_list.append(copy.copy(host))

        new_list.initialized = self.initialized
        return new_list

    # -------------------------------------------------------------------------
    def index(self, host, *args):
        """Return the numeric index of the given host in current list."""
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
            if item == host:
                return index

        if wrap:
            for index in list(range(len(self._list))):
                item = self._list[index]
                if index >= end:
                    break
            if item == host:
                return index

        msg = _("host is not in host list.")
        raise ValueError(msg)

    # -------------------------------------------------------------------------
    def __contains__(self, host):
        """Return whether the given host is contained in current list."""
        if not isinstance(host, VsphereHost):
            raise TypeError(
                self.msg_no_host.format(t=host.__class__.__name__, c=self.__class__.__name__)
            )

        if not self._list:
            return False

        for item in self._list:
            if item == host:
                return True

        return False

    # -------------------------------------------------------------------------
    def count(self, host):
        """Return the number of hosts which are equal to the given one in current list."""
        if not isinstance(host, VsphereHost):
            raise TypeError(
                self.msg_no_host.format(t=host.__class__.__name__, c=self.__class__.__name__)
            )

        if not self._list:
            return 0

        num = 0
        for item in self._list:
            if item == host:
                num += 1
        return num

    # -------------------------------------------------------------------------
    def __len__(self):
        """Return the number of hosts in current list."""
        return len(self._list)

    # -------------------------------------------------------------------------
    def __iter__(self):
        """Iterate through all hosts in current list."""
        for item in self._list:
            yield item

    # -------------------------------------------------------------------------
    def __getitem__(self, key):
        """Get a host from current list by the given numeric index."""
        return self._list.__getitem__(key)

    # -------------------------------------------------------------------------
    def __reversed__(self):
        """Reverse the hosts in list in place."""
        new_list = self.__class__(
            appname=self.appname, verbose=self.verbose, base_dir=self.base_dir, initialized=False
        )

        for host in reversed(self._list):
            new_list.append(copy.copy(host))

        new_list.initialized = self.initialized
        return new_list

    # -------------------------------------------------------------------------
    def __setitem__(self, key, host):
        """Replace the host at the given numeric index by the given one."""
        if not isinstance(host, VsphereHost):
            raise TypeError(
                self.msg_no_host.format(t=host.__class__.__name__, c=self.__class__.__name__)
            )

        self._list.__setitem__(key, host)

    # -------------------------------------------------------------------------
    def __delitem__(self, key):
        """Remove the host at the given numeric index from list."""
        del self._list[key]

    # -------------------------------------------------------------------------
    def append(self, host):
        """Append the given host to the current list."""
        if not isinstance(host, VsphereHost):
            raise TypeError(
                self.msg_no_host.format(t=host.__class__.__name__, c=self.__class__.__name__)
            )

        self._list.append(host)

    # -------------------------------------------------------------------------
    def insert(self, index, host):
        """Insert the given host in current list at given index."""
        if not isinstance(host, VsphereHost):
            raise TypeError(
                self.msg_no_host.format(t=host.__class__.__name__, c=self.__class__.__name__)
            )

        self._list.insert(index, host)

    # -------------------------------------------------------------------------
    def clear(self):
        """Remove all items from the VsphereHostList."""
        self._list = []

    # -------------------------------------------------------------------------
    def ordered(self):
        """Iterate through the hosts in sorted order."""
        try:
            for host in sorted(self._list, key=lambda x: x.name.lower()):
                yield host
        except StopIteration:
            pass


# =============================================================================
if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
