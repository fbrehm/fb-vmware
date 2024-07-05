#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for the application object of the get-vsphere-storage-cluster-list application.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2024 by Frank Brehm, Berlin
"""
from __future__ import absolute_import, print_function

# Standard modules
import logging
import re
import sys

# Third party modules
from fb_tools.argparse_actions import RegexOptionAction
from fb_tools.common import pp
from fb_tools.xlate import format_list

# Own modules
from . import BaseVmwareApplication, VmwareAppError
from .. import __version__ as GLOBAL_VERSION
from ..ds_cluster import VsphereDsCluster, VsphereDsClusterDict
from ..spinner import Spinner
from ..xlate import XLATOR

__version__ = '0.1.0'
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext
ngettext = XLATOR.ngettext

# =============================================================================
class GetVmStorageClustersAppError(VmwareAppError):
    """Base exception class for all exceptions in this application."""

    pass


# =============================================================================
class GetStorageClusterListApp(BaseVmwareApplication):
    """Class for the application object."""

    # -------------------------------------------------------------------------
    def __init__(
        self, appname=None, verbose=0, version=GLOBAL_VERSION, base_dir=None,
            initialized=False, usage=None, description=None,
            argparse_epilog=None, argparse_prefix_chars='-', env_prefix=None):
        """Initialize a GetStorageClusterListApp object."""
        desc = _(
            'Tries to get a list of all datastore clusters in '
            'VMWare VSphere and print it out.')

        self.st_clusters = []

        super(GetStorageClusterListApp, self).__init__(
            appname=appname, verbose=verbose, version=version, base_dir=base_dir,
            description=desc, initialized=False,
        )

        self.initialized = True

    # -------------------------------------------------------------------------
    def _run(self):

        LOG.debug(_('Starting {a!r}, version {v!r} ...').format(
            a=self.appname, v=self.version))

        ret = 0
        try:
            ret = self.get_all_storage_clusters()
        finally:
            self.cleaning_up()

        self.exit(ret)

    # -------------------------------------------------------------------------
    def get_datastore_clusters(self, vsphere_name):
        """Get all datastore clusters in a VMWare VSPhere."""
        storage_clusters = []

        vsphere = self.vsphere[vsphere_name]
        vsphere.get_ds_clusters()

        for cluster in vsphere.ds_clusters:
            storage_clusters.append(vsphere.ds_clusters[cluster])

        return storage_clusters

    # -------------------------------------------------------------------------
    def get_all_storage_clusters(self):
        """Collect all storage clusters."""
        ret = 0
        all_storage_clusters = {}

        # ----------
        def _get_all_storage_clusters():

            for vsphere_name in self.vsphere:
                if vsphere_name not in all_storage_clusters:
                    all_storage_clusters[vsphere_name] = VsphereDsClusterDict()
                for cluster in self.get_datastore_clusters(vsphere_name):
                    all_storage_clusters[vsphere_name].append(cluster)

        if self.verbose or self.quiet:
            _get_all_storage_clusters()

        else:
            spin_prompt = _('Getting all VSPhere storage clusters ...')
            with Spinner(spin_prompt):
                _get_all_storage_clusters()
            sys.stdout.write(' ' * len(spin_prompt))
            sys.stdout.write('\r')
            sys.stdout.flush()

        if self.verbose > 2:
            LOG.debug(_('Found datastore clusters:') + '\n' + pp(all_storage_clusters))

        self.print_clusters(all_storage_clusters)

        return ret

    # -------------------------------------------------------------------------
    def print_clusters(self, clusters):
        """Print on STDOUT all information about all datastore clusters."""
        labels = {
            'cluster_name': 'Cluster',
            'vsphere_name': 'VSPhere',
            'capacity_gb': _('Capacity in GB'),
            'free_space_gb': _('Free space in GB'),
            'calculated_usage': _('Calculated usage in GB'),
            'usage_pc': _('Usage in percent'),
        }
        label_list = (
            'cluster_name', 'vsphere_name', 'capacity_gb',
            'calculated_usage', 'usage_pc', 'free_space_gb')

        str_lengths = {}
        for label in labels.keys():
            str_lengths[label] = len(labels[label])

        max_len = 0
        count = 0

        out = []

        for vsphere_name in clusters.keys():
            for cluster_name in clusters[vsphere_name].keys():

                cl = clusters[vsphere_name][cluster_name]
                cluster = {}

                cluster['cluster_name'] = cluster_name
                if len(cluster_name) > str_lengths['cluster_name']:
                    str_lengths['cluster_name'] = len(cluster_name)

                cluster['vsphere_name'] = vsphere_name
                if len(vsphere_name) > str_lengths['vsphere_name']:
                    str_lengths['vsphere_name'] = len(vsphere_name)

                cap = '{:7.1f}'.format(cl.capacity_gb)
                cluster['capacity_gb'] = cap
                if len(cap) > str_lengths['capacity_gb']:
                    str_lengths['capacity_gb'] = len(cap)

                free = '{:7.1f}'.format(cl.free_space_gb)
                cluster['free_space_gb'] = free
                if len(free) > str_lengths['free_space_gb']:
                    str_lengths['free_space_gb'] = len(free)

                used = cl.capacity_gb - cl.free_space_gb
                used_str = '{:7.1f}'.format(used)
                cluster['calculated_usage'] = used_str
                if len(used_str) > str_lengths['calculated_usage']:
                    str_lengths['calculated_usage'] = len(used_str)

                used_pc = '{:6.2f} %'.format(used / cl.capacity_gb * 100.0)
                cluster['usage_pc'] = used_pc
                if len(used_pc) > str_lengths['usage_pc']:
                    str_lengths['usage_pc'] = len(used_pc)

                out.append(cluster)

        for label in labels:
            if max_len:
                max_len += 2
            max_len += str_lengths[label]

        if self.verbose > 2:
            LOG.debug('Label length:\n' + pp(str_lengths))
            LOG.debug('Max line length: {} chars'.format(max_len))
            LOG.debug('Datastore clusters:\n' + pp(out))


# =============================================================================
if __name__ == '__main__':

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
