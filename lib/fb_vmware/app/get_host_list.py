#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 by Frank Brehm, Berlin
@summary: The module for the application object of the get-vsphere-host-list application.
"""
from __future__ import absolute_import, print_function

# Standard modules
import logging
import re
import sys

from operator import itemgetter

# Third party modules

from fb_tools.common import pp
from fb_tools.argparse_actions import RegexOptionAction
from fb_tools.xlate import format_list

# Own modules
from .. import __version__ as GLOBAL_VERSION

from ..xlate import XLATOR

from ..spinner import Spinner

from . import BaseVmwareApplication, VmwareAppError

__version__ = '0.3.2'
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext
ngettext = XLATOR.ngettext


# =============================================================================
class GetVmHostsAppError(VmwareAppError):
    """ Base exception class for all exceptions in this application."""
    pass


# =============================================================================
class GetHostsListApplication(BaseVmwareApplication):
    """Class for the application object."""

    default_host_pattern = r'.*'
    avail_sort_keys = ('name', 'vsphere', 'cluster', 'vendor', 'model', 'os_version')
    default_sort_keys = ['name', 'vsphere']

    # -------------------------------------------------------------------------
    def __init__(
        self, appname=None, verbose=0, version=GLOBAL_VERSION, base_dir=None,
            initialized=False, usage=None, description=None,
            argparse_epilog=None, argparse_prefix_chars='-', env_prefix=None):

        desc = _(
            "Tries to get a list of all physical hosts in "
            "VMWare VSphere and print it out.")

        self._host_pattern = self.default_host_pattern
        self.sort_keys = self.default_sort_keys

        self.hosts = []

        super(GetHostsListApplication, self).__init__(
            appname=appname, verbose=verbose, version=version, base_dir=base_dir,
            description=desc, initialized=False,
        )

        self.initialized = True

    # -------------------------------------------------------------------------
    @property
    def host_pattern(self):
        """The regex search pattern for filtering the host list."""
        return self._host_pattern

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(GetHostsListApplication, self).as_dict(short=short)
        res['host_pattern'] = self.host_pattern
        res['default_host_pattern'] = self.default_host_pattern

        return res

    # -------------------------------------------------------------------------
    def init_arg_parser(self):
        """
        Public available method to initiate the argument parser.
        """

        super(GetHostsListApplication, self).init_arg_parser()

        filter_group = self.arg_parser.add_argument_group(_('Filter options'))

        filter_group.add_argument(
            '-p', '--pattern', '--search-pattern',
            dest='host_pattern', metavar='REGEX', action=RegexOptionAction,
            topic=_('for names of hosts'), re_options=re.IGNORECASE,
            help=_(
                "A regular expression to filter the output list of hosts by their name "
                "(Default: {!r}).").format(self.default_host_pattern)
        )

        online_filter = filter_group.add_mutually_exclusive_group()
        online_filter.add_argument(
            '--on', '--online', action="store_true", dest="online",
            help=_("Filter output for online hosts.")
        )
        online_filter.add_argument(
            '--off', '--offline', action="store_true", dest="offline",
            help=_("Filter output for offline hosts and templates.")
        )

        output_options = self.arg_parser.add_argument_group(_('Output options'))

        output_options.add_argument(
            '-S', '--sort', metavar='KEY', nargs='+', dest='sort_keys',
            choices=self.avail_sort_keys, help=_(
                "The keys for sorting the output. Available keys are: {avail}. "
                "The default sorting keys are: {default}.").format(
                avail=format_list(self.avail_sort_keys, do_repr=True),
                default=format_list(self.default_sort_keys, do_repr=True))
        )

    # -------------------------------------------------------------------------
    def perform_arg_parser(self):

        super(GetHostsListApplication, self).perform_arg_parser()

        if self.args.host_pattern:
            try:
                re_name = re.compile(self.args.host_pattern, re.IGNORECASE)
                LOG.debug(_("Regular expression for filtering: {!r}").format(re_name.pattern))
                self._host_pattern = self.args.host_pattern
            except Exception as e:
                msg = _("Got a {c} for pattern {p!r}: {e}").format(
                    c=e.__class__.__name__, p=self.args.host_pattern, e=e)
                LOG.error(msg)

        if self.args.sort_keys:
            self.sort_keys = self.args.sort_keys

    # -------------------------------------------------------------------------
    def _run(self):

        LOG.debug(_("Starting {a!r}, version {v!r} ...").format(
            a=self.appname, v=self.version))

        ret = 0
        try:
            ret = self.get_all_hosts()
        finally:
            self.cleaning_up()

        self.exit(ret)

    # -------------------------------------------------------------------------
    def get_all_hosts(self):

        ret = 0
        all_hosts = []

        if self.verbose:
            for vsphere_name in self.vsphere:
                all_hosts += self.get_hosts(vsphere_name)
        elif not self.quiet:
            spin_prompt = _("Getting all VSPhere hosts ...") + ' '
            with Spinner(spin_prompt):
                for vsphere_name in self.vsphere:
                    all_hosts += self.get_hosts(vsphere_name)
            sys.stdout.write(' ' * len(spin_prompt))
            sys.stdout.write('\r')
            sys.stdout.flush()

        first = True
        out_hosts = []

        for host in all_hosts:
            if self.verbose > 1 and first:
                LOG.debug(_("First found host:") + '\n' + pp(host.as_dict()))
            first = False
            is_online = True
            if not host.connection_state or host.maintenance:
                is_online = False
            if not host.online or host.quarantaine:
                is_online = False
            if self.args.online:
                if not is_online:
                    continue
            elif self.args.offline:
                if is_online:
                    continue
            out_hosts.append(self.create_host_summary(host))
        if self.verbose > 1:
            LOG.debug("All hosts:\n{}".format(pp(out_hosts)))

        self.print_hosts(out_hosts)

        return ret

    # -------------------------------------------------------------------------
    def create_host_summary(self, host):

        summary = {}

        summary['vsphere'] = host.vsphere
        summary['cluster'] = host.cluster_name
        summary['name'] = host.name
        summary['connection_state'] = host.connection_state
        cpu_cores = '-'
        if host.cpu_cores:
            cpu_cores = host.cpu_cores
        cpu_threads = '-'
        if host.cpu_threads:
            cpu_threads = host.cpu_threads
        summary['cpus'] = '{co}/{thr}'.format(co=cpu_cores, thr=cpu_threads)
        summary['memory_gb'] = host.memory_gb
        summary['vendor'] = host.vendor
        summary['model'] = host.model
        summary['maintenance'] = host.maintenance
        summary['online'] = host.online
        summary['no_portgroups'] = str(len(host.portgroups))
        summary['power_state'] = host.power_state
        summary['os_name'] = host.product.name
        summary['os_version'] = host.product.os_version
        summary['quarantaine'] = host.quarantaine

        return summary

    # -------------------------------------------------------------------------
    def print_hosts(self, hosts):

        labels = {
            'vsphere': 'VSPhere',
            'cluster': 'Cluster',
            'name': 'Host',
            'connection_state': _("Connect state"),
            'cpus': _("CPU cores/threads"),
            'memory_gb': _("Memory in GiB"),
            'vendor': _('Vendor'),
            'model': _('Model'),
            'maintenance': _('Maintenance'),
            'online': _('Online'),
            # 'no_portgroups': _('Portgroups'),
            'power_state': _('Power State'),
            'os_name': _('OS Name'),
            'os_version': _('OS Version'),
            # 'quarantaine': _('Quarantaine'),
        }

        label_list = (
            'name', 'vsphere', 'cluster', 'vendor', 'model', 'os_name', 'os_version', 'cpus',
            'memory_gb', 'power_state', 'connection_state', 'online',
            'maintenance')

        str_lengths = {}
        for label in labels.keys():
            str_lengths[label] = len(labels[label])

        max_len = 0
        count = 0
        for host in hosts:
            for label in labels.keys():
                val = host[label]
                if val is None:
                    val = '-'
                    host[label] = val
                else:
                    if label == 'memory_gb':
                        val = '{:7.1f}'.format(val)
                        host[label] = val
                    elif label in ('connection_state', 'maintenance', 'online', 'quarantaine'):
                        if val:
                            val = _("Yes")
                        else:
                            val = _("No")
                        host[label] = val
                if len(val) > str_lengths[label]:
                    str_lengths[label] = len(val)

        for label in labels.keys():
            if max_len:
                max_len += 2
            max_len += str_lengths[label]

        if self.verbose > 1:
            LOG.debug("Label length:\n" + pp(str_lengths))
            LOG.debug("Max line length: {} chars".format(max_len))

        tpl = ''
        for label in label_list:
            if tpl != '':
                tpl += '  '
            if label in ('memory_gb', 'cpus', 'no_portgroups'):
                tpl += '{{{la}:>{le}}}'.format(la=label, le=str_lengths[label])
            else:
                tpl += '{{{la}:<{le}}}'.format(la=label, le=str_lengths[label])
        if self.verbose > 1:
            LOG.debug(_("Line template: {}").format(tpl))

        if not self.quiet:
            print()
            print(tpl.format(**labels))
            print('-' * max_len)

        hosts.sort(key=itemgetter(*self.sort_keys))

        for host in hosts:
            count += 1
            print(tpl.format(**host))

        if not self.quiet:
            print()
            if count == 0:
                msg = _("Found no VMWare hosts.")
            else:
                msg = ngettext(
                    "Found one VMWare host.",
                    "Found {} VMWare hosts.", count).format(count)
            print(msg)
            print()

    # -------------------------------------------------------------------------
    def get_hosts(self, vsphere_name):

        hosts = []

        vsphere = self.vsphere[vsphere_name]
        vsphere.get_datacenter()

        re_name = None
        if self.host_pattern is not None:
            re_name = re.compile(self.host_pattern, re.IGNORECASE)

        vsphere.get_hosts(re_name=re_name, vsphere_name=vsphere_name)

        for host_name in sorted(vsphere.hosts.keys()):
            host = vsphere.hosts[host_name]
            hosts.append(host)

        return hosts


# =============================================================================
if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
