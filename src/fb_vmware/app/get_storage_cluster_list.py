#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for the application object of the get-vsphere-storage-cluster-list application.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import absolute_import, print_function

# Standard modules
import logging
import sys
from operator import itemgetter

# Third party modules
from babel.numbers import format_decimal

# from fb_tools.argparse_actions import RegexOptionAction
from fb_tools.common import pp
from fb_tools.spinner import Spinner
from fb_tools.xlate import format_list

# Own modules
from . import BaseVmwareApplication, VmwareAppError
from .. import __version__ as GLOBAL_VERSION
# from ..ds_cluster import VsphereDsCluster
from ..ds_cluster import VsphereDsClusterDict
from ..errors import VSphereExpectedError
from ..xlate import XLATOR

__version__ = '1.1.0'
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

    avail_sort_keys = (
        'cluster_name', 'vsphere_name', 'capacity', 'free_space', 'usage', 'usage_pc')
    default_sort_keys = ['vsphere_name', 'cluster_name']

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
        self._print_total = True
        self.totals = None
        self.sort_keys = self.default_sort_keys

        super(GetStorageClusterListApp, self).__init__(
            appname=appname, verbose=verbose, version=version, base_dir=base_dir,
            description=desc, initialized=False,
        )

        self.initialized = True

    # -------------------------------------------------------------------------
    @property
    def print_total(self):
        """Print out a line with the total capacity."""
        return self._print_total

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transform the elements of the object into a dict.

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """
        res = super(GetStorageClusterListApp, self).as_dict(short=short)
        res['print_total'] = self.print_total

        return res

    # -------------------------------------------------------------------------
    def init_arg_parser(self):
        """Public available method to initiate the argument parser."""
        super(GetStorageClusterListApp, self).init_arg_parser()

        output_options = self.arg_parser.add_argument_group(_('Output options'))

        output_options.add_argument(
            '-N', '--no-totals', action='store_true', dest='no_totals',
            help=_("Don't print the totals of all storage clusters."),
        )

        output_options.add_argument(
            '-S', '--sort', metavar='KEY', nargs='+', dest='sort_keys',
            choices=self.avail_sort_keys, help=_(
                'The keys for sorting the output. Available keys are: {avail}. '
                'The default sorting keys are: {default}.').format(
                avail=format_list(self.avail_sort_keys, do_repr=True),
                default=format_list(self.default_sort_keys, do_repr=True))
        )

    # -------------------------------------------------------------------------
    def perform_arg_parser(self):
        """Evaluate command line parameters."""
        super(GetStorageClusterListApp, self).perform_arg_parser()

        if self.args.sort_keys:
            self.sort_keys = self.args.sort_keys

        if getattr(self.args, 'no_totals', False):
            self._print_total = False

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
        try:
            vsphere.get_ds_clusters()
        except VSphereExpectedError as e:
            LOG.error(str(e))
            self.exit(6)

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
            spinner_name = self.get_random_spinner_name()
            with Spinner(spin_prompt, spinner_name):
                _get_all_storage_clusters()
            sys.stdout.write(' ' * len(spin_prompt))
            sys.stdout.write('\r')
            sys.stdout.flush()

        if self.verbose > 2:
            LOG.debug(_('Found datastore clusters:') + '\n' + pp(all_storage_clusters))

        self.print_clusters(all_storage_clusters)

        return ret

    # -------------------------------------------------------------------------
    def _get_cluster_list(self, clusters):

        cluster_list = []

        total_capacity = 0.0
        total_free = 0.0

        for vsphere_name in clusters.keys():
            for cluster_name in clusters[vsphere_name].keys():

                cl = clusters[vsphere_name][cluster_name]
                cluster = {}
                cluster['is_total'] = False

                cluster['cluster_name'] = cluster_name

                cluster['vsphere_name'] = vsphere_name

                cluster['capacity'] = cl.capacity_gb
                cluster['capacity_gb'] = format_decimal(cl.capacity_gb, format='#,##0')
                total_capacity += cl.capacity_gb

                cluster['free_space'] = cl.free_space_gb
                cluster['free_space_gb'] = format_decimal(cl.free_space_gb, format='#,##0')
                total_free += cl.free_space_gb

                used = cl.capacity_gb - cl.free_space_gb
                cluster['usage'] = used
                cluster['usage_gb'] = format_decimal(used, format='#,##0')

                if cl.capacity_gb:
                    usage_pc = used / cl.capacity_gb
                    cluster['usage_pc'] = usage_pc
                    cluster['usage_pc_out'] = format_decimal(usage_pc, format='0.0 %')
                else:
                    cluster['usage_pc_out'] = '- %'

                cluster_list.append(cluster)

        if self.print_total:
            total_used = total_capacity - total_free
            total_used_pc = None
            total_used_pc_out = '- %'
            if total_capacity:
                total_used_pc = total_used / total_capacity
                total_used_pc_out = format_decimal(total_used_pc, format='0.0 %')

            self.totals = {
                'cluster_name': _('Total'),
                'vsphere_name': '',
                'is_total': True,
                'capacity_gb': format_decimal(total_capacity, format='#,##0'),
                'free_space_gb': format_decimal(total_free, format='#,##0'),
                'usage_gb': format_decimal(total_used, format='#,##0'),
                'usage_pc_out': total_used_pc_out,
            }
            if not self.quiet:
                self.totals['cluster_name'] += ':'

        return cluster_list

    # -------------------------------------------------------------------------
    def _get_cluster_fields_len(self, cluster_list, labels):

        field_length = {}

        for label in labels.keys():
            field_length[label] = len(labels[label])

        for cluster in cluster_list:
            for label in labels.keys():
                field = cluster[label]
                if len(field) > field_length[label]:
                    field_length[label] = len(field)

        if self.totals:
            for label in labels.keys():
                field = self.totals[label]
                if len(field) > field_length[label]:
                    field_length[label] = len(field)

        return field_length

    # -------------------------------------------------------------------------
    def print_clusters(self, clusters):
        """Print on STDOUT all information about all datastore clusters."""
        labels = {
            'cluster_name': 'Cluster',
            'vsphere_name': 'VSPhere',
            'capacity_gb': _('Capacity in GB'),
            'free_space_gb': _('Free space in GB'),
            'usage_gb': _('Calculated usage in GB'),
            'usage_pc_out': _('Usage in percent'),
        }

        label_list = (
            'cluster_name', 'vsphere_name', 'capacity_gb',
            'usage_gb', 'usage_pc_out', 'free_space_gb')

        cluster_list = self._get_cluster_list(clusters)
        field_length = self._get_cluster_fields_len(cluster_list, labels)

        max_len = 0
        count = len(cluster_list)

        for label in labels.keys():
            if max_len:
                max_len += 2
            max_len += field_length[label]

        if self.verbose > 2:
            LOG.debug('Label length:\n' + pp(field_length))
            LOG.debug('Max line length: {} chars'.format(max_len))
            LOG.debug('Datastore clusters:\n' + pp(cluster_list))

        tpl = ''
        for label in label_list:
            if tpl != '':
                tpl += '  '
            if label in ('cluster_name', 'vsphere_name'):
                tpl += '{{{la}:<{le}}}'.format(la=label, le=field_length[label])
            else:
                tpl += '{{{la}:>{le}}}'.format(la=label, le=field_length[label])
        if self.verbose > 1:
            LOG.debug(_('Line template: {}').format(tpl))

        if self.sort_keys:
            LOG.debug('Sorting keys: ' + pp(self.sort_keys))
            self.sort_keys.reverse()
            for key in self.sort_keys:
                if key in ('cluster_name', 'vsphere_name'):
                    cluster_list.sort(key=itemgetter(key))
                else:
                    cluster_list.sort(key=itemgetter(key), reverse=True)

        if not self.quiet:
            print()
            print(tpl.format(**labels))
            print('-' * max_len)

        for cluster in cluster_list:
            print(tpl.format(**cluster))

        if self.totals:
            if not self.quiet:
                print('-' * max_len)
            print(tpl.format(**self.totals))

        if not self.quiet:
            print()
            if count:
                msg = ngettext(
                    'Found one VMWare storage cluster.',
                    'Found {} VMWare storage clusters.'.format(count),
                    count)
            else:
                msg = _('No VMWare storage clusters found.')

            print(msg)
            print()


# =============================================================================
if __name__ == '__main__':

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
