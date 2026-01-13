#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for capsulating a vSphere calculation cluster object.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import absolute_import

# Standard modules
import logging

# Third party modules
from fb_tools.common import is_sequence, pp, to_bool
from fb_tools.xlate import format_list

from pyVmomi import vim

# Own modules
from .errors import VSphereNameError
from .obj import DEFAULT_OBJ_STATUS
from .obj import VsphereObject
from .xlate import XLATOR

__version__ = "1.7.0"
LOG = logging.getLogger(__name__)


_ = XLATOR.gettext


# =============================================================================
class VsphereCluster(VsphereObject):
    """An object for encapsulating a vSphere calculation cluster object."""

    # -------------------------------------------------------------------------
    def __init__(
        self,
        appname=None,
        verbose=0,
        version=__version__,
        base_dir=None,
        initialized=None,
        dc_name=None,
        name=None,
        status=DEFAULT_OBJ_STATUS,
        cpu_cores=0,
        cpu_threads=0,
        config_status=DEFAULT_OBJ_STATUS,
        hosts_effective=0,
        hosts_total=0,
        mem_mb_effective=0,
        mem_total=0,
        standalone=False,
    ):
        """Initialize a VsphereCluster object."""
        self.repr_fields = (
            "dc_name",
            "name",
            "status",
            "config_status",
            "cpu_cores",
            "cpu_threads",
            "hosts_effective",
            "hosts_total",
            "mem_mb_effective",
            "mem_total",
            "appname",
            "verbose",
            "version",
        )

        self._status = None
        self._cpu_cores = None
        self._cpu_threads = None
        self._hosts_effective = None
        self._hosts_total = None
        self._mem_mb_effective = None
        self._mem_total = None
        self._standalone = False
        self._dc_name = None
        self.networks = []
        self.datastores = []
        self.resource_pool = None

        super(VsphereCluster, self).__init__(
            name=name,
            obj_type="vsphere_cluster",
            name_prefix="cluster",
            status=status,
            config_status=config_status,
            appname=appname,
            verbose=verbose,
            version=version,
            base_dir=base_dir,
        )

        self.dc_name = dc_name
        self.cpu_cores = cpu_cores
        self.cpu_threads = cpu_threads
        self.hosts_effective = hosts_effective
        self.hosts_total = hosts_total
        self.mem_mb_effective = mem_mb_effective
        self.mem_total = mem_total
        self.standalone = standalone

        if initialized is not None:
            self.initialized = initialized

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
    def resource_pool_name(self):
        """Return the name of the default resource pool of this cluster."""
        return self.name + "/Resources"

    # -----------------------------------------------------------
    @property
    def resource_pool_var(self):
        """Return the variable name of the default resource pool used for terraform."""
        return "pool_" + self.tf_name

    # -----------------------------------------------------------
    @property
    def cpu_cores(self):
        """Return the number of physical CPU cores of the cluster."""
        return self._cpu_cores

    @cpu_cores.setter
    def cpu_cores(self, value):
        if value is None:
            self._cpu_cores = 0
            return

        val = int(value)
        self._cpu_cores = val

    # -----------------------------------------------------------
    @property
    def cpu_threads(self):
        """Return the aggregated number of CPU threads of the cluster."""
        return self._cpu_threads

    @cpu_threads.setter
    def cpu_threads(self, value):
        if value is None:
            self._cpu_threads = 0
            return

        val = int(value)
        self._cpu_threads = val

    # -----------------------------------------------------------
    @property
    def hosts_effective(self):
        """Return the total number of effective hosts of the cluster."""
        return self._hosts_effective

    @hosts_effective.setter
    def hosts_effective(self, value):
        if value is None:
            self._hosts_effective = 0
            return

        val = int(value)
        self._hosts_effective = val

    # -----------------------------------------------------------
    @property
    def hosts_total(self):
        """Return the total number of hosts of the cluster."""
        return self._hosts_total

    @hosts_total.setter
    def hosts_total(self, value):
        if value is None:
            self._hosts_total = 0
            return

        val = int(value)
        self._hosts_total = val

    # -----------------------------------------------------------
    @property
    def mem_total(self):
        """Return the aggregated memory resources of all hosts of the cluster in Bytes."""
        return self._mem_total

    @mem_total.setter
    def mem_total(self, value):
        if value is None:
            self._mem_total = 0
            return

        val = int(value)
        self._mem_total = val

    # -----------------------------------------------------------
    @property
    def mem_mb_total(self):
        """Return the aggregated memory resources of all hosts of the cluster in MiBytes."""
        if self.mem_total is None:
            return None
        return self.mem_total / 1024 / 1024

    # -----------------------------------------------------------
    @property
    def mem_gb_total(self):
        """Return the aggregated memory resources of all hosts of the cluster in GiBytes."""
        if self.mem_total is None:
            return None
        return float(self.mem_total) / 1024.0 / 1024.0 / 1024.0

    # -----------------------------------------------------------
    @property
    def mem_mb_effective(self):
        """Return the effective memory resources (in MB) available to run VMs of the cluster."""
        return self._mem_mb_effective

    @mem_mb_effective.setter
    def mem_mb_effective(self, value):
        if value is None:
            self._mem_mb_effective = 0
            return

        val = int(value)
        self._mem_mb_effective = val

    # -----------------------------------------------------------
    @property
    def mem_gb_effective(self):
        """Return the effective memory resources (in GiB) available to run VMs of the cluster."""
        if self.mem_mb_effective is None:
            return None
        return float(self.mem_mb_effective) / 1024.0

    # -----------------------------------------------------------
    @property
    def standalone(self):
        """Return whether this a standalone host and not a computing cluster."""
        return self._standalone

    @standalone.setter
    def standalone(self, value):
        self._standalone = to_bool(value)

    # -----------------------------------------------------------
    def get_pyvmomi_obj(self, service_instance):
        """Return the appropriate PyVMomi object for the current object."""
        obj = None
        if not self.name:
            return None

        content = service_instance.RetrieveContent()
        container = content.viewManager.CreateContainerView(
            content.rootFolder, vim.ClusterComputeResource, True
        )
        for c in container.view:
            if c.name == self.name:
                obj = c
                break

        if obj is not None:
            return obj

        content = service_instance.RetrieveContent()
        container = content.viewManager.CreateContainerView(
            content.rootFolder, vim.ComputeResource, True
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
        res = super(VsphereCluster, self).as_dict(short=short)

        res["dc_name"] = self.dc_name
        res["resource_pool_name"] = self.resource_pool_name
        res["resource_pool_var"] = self.resource_pool_var
        res["cpu_cores"] = self.cpu_cores
        res["cpu_threads"] = self.cpu_threads
        res["hosts_effective"] = self.hosts_effective
        res["hosts_total"] = self.hosts_total
        res["mem_mb_effective"] = self.mem_mb_effective
        res["mem_gb_effective"] = self.mem_gb_effective
        res["mem_total"] = self.mem_total
        res["mem_mb_total"] = self.mem_mb_total
        res["mem_gb_total"] = self.mem_gb_total
        res["standalone"] = self.standalone
        res["resource_pool.summary"] = None
        if self.resource_pool:
            if self.verbose > 3:
                res["resource_pool.summary"] = self.resource_pool.summary
            else:
                res["resource_pool.summary"] = "{} object".format(
                    self.resource_pool.summary.__class__.__name__
                )

        return res

    # -------------------------------------------------------------------------
    def __copy__(self):
        """Magic method to return a deep copy of the current object."""
        return VsphereCluster(
            appname=self.appname,
            verbose=self.verbose,
            base_dir=self.base_dir,
            initialized=self.initialized,
            name=self.name,
            dc_name=self.dc_name,
            standalone=self.standalone,
            status=self.status,
            cpu_cores=self.cpu_cores,
            cpu_threads=self.cpu_threads,
            hosts_effective=self.hosts_effective,
            hosts_total=self.hosts_total,
            mem_mb_effective=self.mem_mb_effective,
            mem_total=self.mem_total,
        )

    # -------------------------------------------------------------------------
    def __eq__(self, other):
        """Use this magic method as the '=='-operator."""
        if self.verbose > 4:
            LOG.debug(_("Comparing {} objects ...").format(self.__class__.__name__))

        if not isinstance(other, VsphereCluster):
            return False

        if self.dc_name != other.dc_name:
            return False

        if self.name != other.name:
            return False

        return True

    # -------------------------------------------------------------------------
    @classmethod
    def from_summary(
        cls, data, dc_name=None, appname=None, verbose=0, base_dir=None, test_mode=False
    ):
        """Create a new VsphereCluster object based on the appropriate data from pyvomi."""
        if test_mode:
            cls._check_summary_data(data)
        else:
            if not isinstance(data, (vim.ClusterComputeResource, vim.ComputeResource)):
                msg = _(
                    "Parameter {t!r} must be a {e} object, a {v} object was given " "instead."
                ).format(t="data", e="vim.AboutInfo", v=data.__class__.__qualname__)
                raise TypeError(msg)

        params = {
            "appname": appname,
            "verbose": verbose,
            "base_dir": base_dir,
            "initialized": True,
            "dc_name": dc_name,
            "name": data.name,
            "status": data.overallStatus,
            "config_status": data.configStatus,
            "cpu_cores": data.summary.numCpuCores,
            "cpu_threads": data.summary.numCpuThreads,
            "hosts_effective": data.summary.numEffectiveHosts,
            "hosts_total": data.summary.numHosts,
            "mem_mb_effective": data.summary.effectiveMemory,
            "mem_total": data.summary.totalMemory,
            "standalone": True,
        }
        if isinstance(data, vim.ClusterComputeResource):
            params["standalone"] = False

        if verbose > 2:
            LOG.debug(_("Creating {} object from:").format(cls.__name__) + "\n" + pp(params))

        cluster = cls(**params)

        for network in data.network:
            nname = network.name
            if nname not in cluster.networks:
                if verbose > 2:
                    LOG.debug(
                        _("Cluster {c!r} has network {n!r}.").format(c=cluster.name, n=nname)
                    )
                cluster.networks.append(nname)

        for ds in data.datastore:
            if ds.name not in cluster.datastores:
                if verbose > 2:
                    LOG.debug(
                        _("Cluster {c!r} has datastore {d!r}.").format(c=cluster.name, d=ds.name)
                    )
                cluster.datastores.append(ds.name)

        cluster.resource_pool = data.resourcePool

        return cluster

    # -------------------------------------------------------------------------
    @classmethod
    def _check_summary_data(cls, data):

        necessary_fields = (
            "datastore",
            "name",
            "network",
            "overallStatus",
            "configStatus",
            "summary",
            "resourcePool",
        )
        summary_fields = (
            "numCpuCores",
            "numCpuThreads",
            "numEffectiveHosts",
            "numHosts",
            "effectiveMemory",
            "totalMemory",
        )
        failing_fields = []

        for field in necessary_fields:
            if not hasattr(data, field):
                failing_fields.append(field)

        if hasattr(data, "summary"):
            summary = data.summary
            for field in summary_fields:
                if not hasattr(summary, field):
                    failing_fields.append("summary.{}".format(field))

        if hasattr(data, "datastore"):
            if not is_sequence(data.datastore):
                msg = _(
                    "The given parameter {p!r} on calling method {m}() is not a sequence " "type."
                ).format(p="data.datastore", m="from_summary")
                raise AssertionError(msg)

        if hasattr(data, "network"):
            if not is_sequence(data.network):
                msg = _(
                    "The given parameter {p!r} on calling method {m}() is not a sequence " "type."
                ).format(p="data.network", m="from_summary")
                raise AssertionError(msg)

        if hasattr(data, "resourcePool") and data.resourcePool:
            if not hasattr(data.resourcePool, "summary"):
                failing_fields.append("data.resourcePool.summary")

        if len(failing_fields):
            msg = _(
                "The given parameter {p!r} on calling method {m}() has failing " "attributes"
            ).format(p="data", m="from_summary")
            msg += ": " + format_list(failing_fields, do_repr=True)
            raise AssertionError(msg)


# =============================================================================
if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
