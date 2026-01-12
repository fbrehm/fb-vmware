#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for a vSphere datastore cluster object.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import absolute_import

# Standard modules
import logging

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
from .datastore import VsphereDatastore
from .datastore import VsphereDatastoreDict
from .errors import VSphereHandlerError
from .errors import VSphereNameError
from .obj import VsphereObject
from .xlate import XLATOR

__version__ = "1.7.0"
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext


# =============================================================================
class VsphereDsCluster(VsphereObject):
    """A wrapper for a Datastore cluster (dsPod)."""

    repr_fields = (
        "name",
        "vsphere",
        "dc_name",
        "status",
        "config_status",
        "capacity",
        "free_space",
        "appname",
        "verbose",
        "version",
    )

    valid_storage_types = (
        'SSD',
        'HDD',
    )

    default_storage_type = 'HDD'

    # -------------------------------------------------------------------------
    def __init__(
        self,
        appname=None,
        verbose=0,
        version=__version__,
        base_dir=None,
        initialized=None,
        name=None,
        vsphere=None,
        dc_name=None,
        status="gray",
        config_status="gray",
        capacity=None,
        free_space=None,
    ):
        """Initialize a VsphereDsCluster object."""
        self._vsphere = None
        self._dc_name = None
        self._capacity = int(capacity)
        self._free_space = int(free_space)
        self.datastores = None
        self.hosts = None
        self.compute_clusters = None

        self._calculated_usage = 0.0
        self._storage_type = self.default_storage_type

        super(VsphereDsCluster, self).__init__(
            name=name,
            obj_type="vsphere_datastore_cluster",
            name_prefix="dspod",
            status=status,
            config_status=config_status,
            appname=appname,
            verbose=verbose,
            version=version,
            base_dir=base_dir,
        )

        self.vsphere = vsphere
        self.dc_name = dc_name

        st_type = self.storage_type_by_name(self.name)
        if st_type:
            self._storage_type = st_type

        if initialized is not None:
            self.initialized = initialized

    # -----------------------------------------------------------
    @property
    def capacity(self):
        """Maximum capacity of this datastore cluster, in bytes."""
        return self._capacity

    # -----------------------------------------------------------
    @property
    def capacity_gb(self):
        """Maximum capacity of this datastore cluster, in GiBytes."""
        return float(self.capacity) / 1024.0 / 1024.0 / 1024.0

    # -----------------------------------------------------------
    @property
    def dc_name(self):
        """Return the datacenter name of the datastore cluster."""
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
    def free_space(self):
        """Available space of this datastore cluster, in bytes."""
        return self._free_space

    # -----------------------------------------------------------
    @property
    def free_space_gb(self):
        """Available space of this datastore cluster, in GiBytes."""
        return float(self._free_space) / 1024.0 / 1024.0 / 1024.0

    # -----------------------------------------------------------
    @property
    def calculated_usage(self):
        """Return the calculated additional usage of this datastore cluster, in GiBytes."""
        return self._calculated_usage

    @calculated_usage.setter
    def calculated_usage(self, value):
        val = float(value)
        self._calculated_usage = val

    # -----------------------------------------------------------
    @property
    def avail_space_gb(self):
        """Available space of datastore cluster in GiB in respect of calculated space."""
        if not self.free_space:
            return 0.0
        if not self.calculated_usage:
            return self.free_space_gb
        return self.free_space_gb - self.calculated_usage

    # -----------------------------------------------------------
    @property
    def vsphere(self):
        """Return the name of the vSphere of the datastore cluster."""
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
    def storage_type(self):
        """Return the type of storage volume, such as HDD or SSD."""
        return self._storage_type

    # -------------------------------------------------------------------------
    @classmethod
    def storage_type_by_name(cls, name):
        """Guess the storage type by its name. May be overridden in descentant classes."""
        if "-sas-" in name.lower():
            return "HDD"

        if "-ssd-" in name.lower():
            return "SSD"

        if "-sata-" in name.lower():
            return "HDD"

        if "-hdd-" in name.lower():
            return "HDD"

        return None

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
        detailled=False,
    ):
        """Create a new VsphereDsCluster object based on the data given from pyvmomi."""
        if test_mode:

            necessary_fields = ("summary", "overallStatus", "configStatus")
            summary_fields = ("capacity", "freeSpace", "name")

            failing_fields = []

            for field in necessary_fields:
                if not hasattr(data, field):
                    failing_fields.append(field)

            if hasattr(data, "summary") and data.summary:
                summary = data.summary
                for field in summary_fields:
                    if not hasattr(summary, field):
                        failing_fields.append("summary." + field)

            if len(failing_fields):
                msg = _(
                    "The given parameter {p!r} on calling method {m}() has failing " "attributes"
                ).format(p="data", m="from_summary")
                msg += ": " + format_list(failing_fields, do_repr=True)
                raise AssertionError(msg)

        else:

            if not isinstance(data, vim.StoragePod):
                msg = _("Parameter {t!r} must be a {e}, {v!r} was given.").format(
                    t="data", e="vim.StoragePod", v=data
                )
                raise TypeError(msg)

        params = {
            "vsphere": vsphere,
            "dc_name": dc_name,
            "appname": appname,
            "verbose": verbose,
            "base_dir": base_dir,
            "initialized": True,
            "capacity": data.summary.capacity,
            "free_space": data.summary.freeSpace,
            "name": data.summary.name,
            "status": data.overallStatus,
            "config_status": data.configStatus,
        }

        if verbose > 2:
            LOG.debug(_("Creating {} object from:").format(cls.__name__) + "\n" + pp(params))
        cluster = cls(**params)

        if detailled:
            cluster.get_detailled_info(data)

        return cluster

    # -----------------------------------------------------------
    def get_detailled_info(self, data):
        """Get detailled infos about owning datastores and connected hosts."""
        if not hasattr(data, "childEntity"):
            return

        self.datastores = VsphereDatastoreDict()
        self.hosts = set()
        self.compute_clusters = set()

        hostlist = {}

        for child in data.childEntity:
            if isinstance(child, vim.Datastore):
                if self.verbose > 1:
                    LOG.debug(
                        _("Datastore {ds!r} is assigned to datastore_cluster {dsc!r}.").format(
                            ds=child.name, dsc=self.name
                        )
                    )
                ds = VsphereDatastore.from_summary(
                    child,
                    vsphere=self.vsphere,
                    dc_name=self.dc_name,
                    cluster=self.name,
                    appname=self.appname,
                    verbose=self.verbose,
                    base_dir=self.base_dir,
                    detailled=True,
                    hostlist=hostlist,
                )
                self.datastores.append(ds)

                for host in ds.hosts:
                    self.hosts.add(host)

                if ds.compute_clusters:
                    for compute_cluster in ds.compute_clusters:
                        self.compute_clusters.add(compute_cluster)

    # -----------------------------------------------------------
    def get_pyvmomi_obj(self, service_instance):
        """Return the appropriate PyVMomi object for the current object."""
        obj = None
        if not self.name:
            return None

        content = service_instance.RetrieveContent()
        container = content.viewManager.CreateContainerView(
            content.rootFolder, vim.StoragePod, True
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
        res = super(VsphereDsCluster, self).as_dict(short=short)
        res["avail_space_gb"] = self.avail_space_gb
        res["calculated_usage"] = self.calculated_usage
        res["capacity"] = self.capacity
        res["capacity_gb"] = self.capacity_gb
        res["dc_name"] = self.dc_name
        res["free_space"] = self.free_space
        res["free_space_gb"] = self.free_space_gb
        res["storage_type"] = self.storage_type
        res["vsphere"] = self.vsphere

        return res

    # -------------------------------------------------------------------------
    def __copy__(self):
        """Return a new VsphereDsCluster as a deep copy of the current object."""
        return VsphereDsCluster(
            vsphere=self.vsphere,
            dc_name=self.dc_name,
            appname=self.appname,
            verbose=self.verbose,
            base_dir=self.base_dir,
            initialized=self.initialized,
            name=self.name,
            status=self.status,
            config_status=self.config_status,
            capacity=self.capacity,
            free_space=self.free_space,
        )

    # -------------------------------------------------------------------------
    def __eq__(self, other):
        """Magic method for using it as the '=='-operator."""
        if self.verbose > 4:
            LOG.debug(_("Comparing {} objects ...").format(self.__class__.__name__))

        if not isinstance(other, VsphereDsCluster):
            return False

        if self.vsphere != other.vsphere:
            return False

        if self.dc_name != other.dc_name:
            return False

        if self.name != other.name:
            return False

        return True


# =============================================================================
class VsphereDsClusterDict(MutableMapping, FbGenericBaseObject):
    """
    A dictionary containing VsphereDsCluster objects.

    It works like a dict.
    """

    msg_invalid_cluster_type = _("Invalid item type {{!r}} to set, only {} allowed.").format(
        "VsphereDsCluster"
    )
    msg_key_not_name = _("The key {k!r} must be equal to the datastore cluster name {n!r}.")
    msg_none_type_error = _("None type as key is not allowed.")
    msg_empty_key_error = _("Empty key {!r} is not allowed.")
    msg_no_cluster_dict = _("Object {{!r}} is not a {} object.").format("VsphereDsClusterDict.")

    # -------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Initialize a VsphereDsClusterDict object."""
        self._map = {}

        for arg in args:
            self.append(arg)

    # -------------------------------------------------------------------------
    def _set_item(self, key, cluster):

        if not isinstance(cluster, VsphereDsCluster):
            raise TypeError(self.msg_invalid_cluster_type.format(cluster.__class__.__name__))

        cluster_name = cluster.name
        if cluster_name != key:
            raise KeyError(self.msg_key_not_name.format(k=key, n=cluster_name))

        self._map[cluster_name] = cluster

    # -------------------------------------------------------------------------
    def append(self, cluster):
        """Set the given datastore cluster in the current dict with its name as key."""
        if not isinstance(cluster, VsphereDsCluster):
            raise TypeError(self.msg_invalid_cluster_type.format(cluster.__class__.__name__))
        self._set_item(cluster.name, cluster)

    # -------------------------------------------------------------------------
    def _get_item(self, key):

        if key is None:
            raise TypeError(self.msg_none_type_error)

        cluster_name = str(key).strip()
        if cluster_name == "":
            raise ValueError(self.msg_empty_key_error.format(key))

        return self._map[cluster_name]

    # -------------------------------------------------------------------------
    def get(self, key):
        """Get the datastore cluster from dict by its name."""
        return self._get_item(key)

    # -------------------------------------------------------------------------
    def _del_item(self, key, strict=True):

        if key is None:
            raise TypeError(self.msg_none_type_error)

        cluster_name = str(key).strip()
        if cluster_name == "":
            raise ValueError(self.msg_empty_key_error.format(key))

        if not strict and cluster_name not in self._map:
            return

        del self._map[cluster_name]

    # -------------------------------------------------------------------------
    # The next five methods are requirements of the ABC.
    def __setitem__(self, key, value):
        """Set the given datastore cluster in the current dict by key."""
        self._set_item(key, value)

    # -------------------------------------------------------------------------
    def __getitem__(self, key):
        """Get the datastore cluster from dict by the key."""
        return self._get_item(key)

    # -------------------------------------------------------------------------
    def __delitem__(self, key):
        """Remove the datastore cluster from dict by the key."""
        self._del_item(key)

    # -------------------------------------------------------------------------
    def __iter__(self):
        """Iterate through datastore cluster names as keys."""
        for cluster_name in self.keys():
            yield cluster_name

    # -------------------------------------------------------------------------
    def __len__(self):
        """Return the number of datastore clusters in current dict."""
        return len(self._map)

    # -------------------------------------------------------------------------
    # The next methods aren't required, but nice for different purposes:
    def __str__(self):
        """Return simple dict representation of the mapping."""
        return str(self._map)

    # -------------------------------------------------------------------------
    def __repr__(self):
        """Transform into a string for reproduction."""
        return "{}, {}({})".format(
            super(VsphereDsClusterDict, self).__repr__(), self.__class__.__name__, self._map
        )

    # -------------------------------------------------------------------------
    def __contains__(self, key):
        """Return whether the given datastore cluster name is contained in this dict as a key."""
        if key is None:
            raise TypeError(self.msg_none_type_error)

        cluster_name = str(key).strip()
        if cluster_name == "":
            raise ValueError(self.msg_empty_key_error.format(key))

        return cluster_name in self._map

    # -------------------------------------------------------------------------
    def keys(self):
        """Return all datastore cluster names of this dict in a sorted manner."""
        return sorted(self._map.keys(), key=str.lower)

    # -------------------------------------------------------------------------
    def items(self):
        """Return tuples (ds cluster name + object as tuple) of this dict in a sorted manner."""
        item_list = []

        for cluster_name in self.keys():
            item_list.append((cluster_name, self._map[cluster_name]))

        return item_list

    # -------------------------------------------------------------------------
    def values(self):
        """Return all datastore cluster objects of this dict."""
        value_list = []
        for cluster_name in self.keys():
            value_list.append(self._map[cluster_name])
        return value_list

    # -------------------------------------------------------------------------
    def __eq__(self, other):
        """Magic method for using it as the '=='-operator."""
        if not isinstance(other, VsphereDsClusterDict):
            raise TypeError(self.msg_no_cluster_dict.format(other))

        return self._map == other._map

    # -------------------------------------------------------------------------
    def __ne__(self, other):
        """Magic method for using it as the '!='-operator."""
        if not isinstance(other, VsphereDsClusterDict):
            raise TypeError(self.msg_no_cluster_dict.format(other))

        return self._map != other._map

    # -------------------------------------------------------------------------
    def pop(self, key, *args):
        """Get the datastore cluster by its name and remove it in dict."""
        if key is None:
            raise TypeError(self.msg_none_type_error)

        cluster_name = str(key).strip()
        if cluster_name == "":
            raise ValueError(self.msg_empty_key_error.format(key))

        return self._map.pop(cluster_name, *args)

    # -------------------------------------------------------------------------
    def popitem(self):
        """Remove and return a arbitrary (ds cluster name and object) pair from the dictionary."""
        if not len(self._map):
            return None

        cluster_name = self.keys()[0]
        cluster = self._map[cluster_name]
        del self._map[cluster_name]
        return (cluster_name, cluster)

    # -------------------------------------------------------------------------
    def clear(self):
        """Remove all items from the dictionary."""
        self._map = {}

    # -------------------------------------------------------------------------
    def setdefault(self, key, default):
        """
        Return the datastore cluster, if the key is in dict.

        If not, insert key with a value of default and return default.
        """
        if key is None:
            raise TypeError(self.msg_none_type_error)

        cluster_name = str(key).strip()
        if cluster_name == "":
            raise ValueError(self.msg_empty_key_error.format(key))

        if not isinstance(default, VsphereDsCluster):
            raise TypeError(self.msg_invalid_cluster_type.format(default.__class__.__name__))

        if cluster_name in self._map:
            return self._map[cluster_name]

        self._set_item(cluster_name, default)
        return default

    # -------------------------------------------------------------------------
    def update(self, other):
        """Update the dict with the key/value pairs from other, overwriting existing keys."""
        if isinstance(other, VsphereDsClusterDict) or isinstance(other, dict):
            for cluster_name in other.keys():
                self._set_item(cluster_name, other[cluster_name])
            return

        for tokens in other:
            key = tokens[0]
            value = tokens[1]
            self._set_item(key, value)

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """Transform the elements of the object into a dict."""
        res = {}
        for cluster_name in self._map:
            res[cluster_name] = self._map[cluster_name].as_dict(short)
        return res

    # -------------------------------------------------------------------------
    def as_list(self, short=True):
        """Return a list with all datastore clusters transformed to a dict."""
        res = []
        for cluster_name in self.keys():
            res.append(self._map[cluster_name].as_dict(short))
        return res


# =============================================================================

if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
