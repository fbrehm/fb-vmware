#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for the application object of the get-vsphere-network-list application.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import absolute_import, print_function

# Standard modules
import logging
import sys
from operator import itemgetter

# from fb_tools.argparse_actions import RegexOptionAction
from fb_tools.common import pp
from fb_tools.spinner import Spinner

# Own modules
from . import BaseVmwareApplication, VmwareAppError
from .. import __version__ as GLOBAL_VERSION
from ..errors import VSphereExpectedError
from ..network import GeneralNetworksDict
from ..network import VsphereNetwork
from ..xlate import XLATOR

__version__ = '1.5.1'
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext
ngettext = XLATOR.ngettext

# =============================================================================
class GetVmNetworkAppError(VmwareAppError):
    """Base exception class for all exceptions in this application."""

    pass


# =============================================================================
class GetNetworkListApp(BaseVmwareApplication):
    """Class for the application object."""

    # -------------------------------------------------------------------------
    def __init__(
        self, appname=None, verbose=0, version=GLOBAL_VERSION, base_dir=None,
            initialized=False, usage=None, description=None,
            argparse_epilog=None, argparse_prefix_chars='-', env_prefix=None):
        """Initialize a GetNetworkListApp object."""
        desc = _(
            'Tries to get a list of all networks in '
            'VMWare VSphere and print it out.')

        self.all_dvpgs = GeneralNetworksDict()
        self.all_networks = GeneralNetworksDict()

        super(GetNetworkListApp, self).__init__(
            appname=appname, verbose=verbose, version=version, base_dir=base_dir,
            description=desc, initialized=False,
        )

        self.initialized = True

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transform the elements of the object into a dict.

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """
        res = super(GetNetworkListApp, self).as_dict(short=short)

        return res

    # -------------------------------------------------------------------------
    def _run(self):

        LOG.debug(_('Starting {a!r}, version {v!r} ...').format(
            a=self.appname, v=self.version))

        VsphereNetwork.warn_unassigned_net = False

        ret = 0
        try:
            ret = self.get_all_networks()
            self.print_virtual_switches()
            self.print_dv_portgroups()
            self.print_networks()
        finally:
            self.cleaning_up()

        self.exit(ret)

    # -------------------------------------------------------------------------
    def get_networks(self, vsphere_name):
        """Get all networks in a VMWare VSPhere."""
        networks = []

        vsphere = self.vsphere[vsphere_name]
        try:
            vsphere.get_networks()

        except VSphereExpectedError as e:
            LOG.error(str(e))
            self.exit(6)

        for network in vsphere.networks:
            networks.append(vsphere.networks[network])

        return networks

    # -------------------------------------------------------------------------
    def _get_all_networks(self):

        for vsphere_name in self.vsphere:
            vsphere = self.vsphere[vsphere_name]
            LOG.debug(_('Get all network-like objects from VSPhere {!r} ...').format(vsphere_name))

            try:
                vsphere.get_networks()
            except VSphereExpectedError as e:
                LOG.error(str(e))
                self.exit(6)

            self.all_dvpgs[vsphere_name] = vsphere.dv_portgroups
            self.all_networks[vsphere_name] = vsphere.networks

    # -------------------------------------------------------------------------
    def get_all_networks(self):
        """Collect all networks."""
        ret = 0

        if self.verbose or self.quiet:
            self._get_all_networks()

        else:
            spin_prompt = _('Getting all VSPhere networks') + ' '
            spinner_name = self.get_random_spinner_name()
            with Spinner(spin_prompt, spinner_name):
                self._get_all_networks()
            sys.stdout.write(' ' * len(spin_prompt))
            sys.stdout.write('\r')
            sys.stdout.flush()

        if self.verbose > 2:
            dvs = {}
            for vsphere_name in self.vsphere:
                dvs[vsphere_name] = {}
                for uuid in self.vsphere[vsphere_name].dvs.keys():
                    dvs[vsphere_name][uuid] = self.vsphere[vsphere_name].dvs[uuid].as_dict()

            msg = _('Found Distributed Virtual Switches:') + '\n' + pp(dvs)
            LOG.debug(msg)

        if self.verbose > 2:
            networks = {}
            dv_port_groups = {}
            if self.verbose > 3:
                dv_port_groups = self.all_dvpgs.as_dict()
                networks = self.all_networks.as_dict()
            else:
                dv_port_group_lists = self.all_dvpgs.as_lists()
                networks_lists = self.all_networks.as_lists()
                for vsphere_name in self.vsphere:
                    dv_port_groups[vsphere_name] = []
                    networks[vsphere_name] = []
                    if len(dv_port_group_lists[vsphere_name]):
                        dv_port_groups[vsphere_name] = [dv_port_group_lists[vsphere_name][0]]
                    if len(networks_lists[vsphere_name]):
                        networks[vsphere_name] = [networks_lists[vsphere_name][0]]

            msg = _('Found Distributed Virtual Portgroups:') + pp(dv_port_groups)
            LOG.debug(msg)
            msg = _('Found Virtual Networks:') + pp(networks)
            LOG.debug(msg)

        return ret

    # -------------------------------------------------------------------------
    def print_virtual_switches(self):
        """Print on STDOUT all information about Distributed Virtual Switches."""
        all_dvs = []

        print()
        title = _('Distributed Virtual Switches')
        print(self.colored(title, 'cyan'))
        print(self.colored('=' * len(title), 'cyan'))

        # -----------------------------
        def get_contact(dvs):
            """Generate and return a contact string for this DVS."""
            contact_name = None
            contact_info = None
            contact = '~'
            if dvs.contact_name is not None:
                contact_name = dvs.contact_name.strip()
            if dvs.contact_info is not None:
                contact_info = dvs.contact_info.strip()
            if contact_name:
                if contact_info:
                    contact = '{n} ({i})'.format(n=contact_name, i=contact_info)
                else:
                    contact = contact_name
            elif contact_info:
                contact = contact_info

            return contact

        for vsphere_name in self.vsphere:
            for uuid in self.vsphere[vsphere_name].dvs.keys():
                this_dvs = self.vsphere[vsphere_name].dvs[uuid]

                dvs = {
                    'vsphere': vsphere_name,
                    'name': this_dvs.name,
                    'contact': get_contact(this_dvs),
                    'create_time': this_dvs.create_time.isoformat(sep=' ', timespec='seconds'),
                    'description': this_dvs.description,
                    'hosts': '{:,}'.format(this_dvs.num_hosts),
                    'ports': '{:,}'.format(this_dvs.num_ports),
                    'standalone_ports': '{:,}'.format(this_dvs.num_standalone_ports),
                    'ratio_reservation': '{:d} %'.format(this_dvs.pnic_cap_ratio_reservation),
                }
                all_dvs.append(dvs)

        if len(all_dvs):
            self._print_virtual_switches(all_dvs)
            return

        print()
        print(_('No Distributed Virtual Switches found.'))

    # -------------------------------------------------------------------------
    def _print_virtual_switches(self, all_dvs):

        labels = {
            'vsphere': 'VSPhere',
            'name': _('Name'),
            'contact': _('Contact'),
            'create_time': _('Creation time'),
            'description': _('Description'),
            'hosts': _('Hosts'),
            'ports': _('Ports'),
            'standalone_ports': _('Standalone Ports'),
            'ratio_reservation': _('Ratio reservation'),
        }
        label_list = (
            'name', 'vsphere', 'create_time', 'hosts', 'ports', 'standalone_ports',
            'ratio_reservation', 'contact', 'description',
        )

        str_lengths = {}
        for label in labels:
            str_lengths[label] = len(labels[label])

        max_len = 0
        count = 0
        for dvs in all_dvs:
            for label in labels.keys():
                val = dvs[label]
                if val is None:
                    val = '-'
                    dvs[label] = val
                if len(val) > str_lengths[label]:
                    str_lengths[label] = len(val)

        for label in labels.keys():
            if max_len:
                max_len += 2
            max_len += str_lengths[label]

        if self.verbose > 1:
            LOG.debug('Label length:\n' + pp(str_lengths))
            LOG.debug('Max line length: {} chars'.format(max_len))

        tpl = ''
        for label in label_list:
            if tpl != '':
                tpl += '  '
            if label in ('hosts', 'ports', 'standalone_ports', 'ratio_reservation'):
                tpl += '{{{la}:>{le}}}'.format(la=label, le=str_lengths[label])
            else:
                tpl += '{{{la}:<{le}}}'.format(la=label, le=str_lengths[label])
        if self.verbose > 1:
            LOG.debug(_('Line template: {}').format(tpl))

        if not self.quiet:
            print()
            print(tpl.format(**labels))
            print('-' * max_len)

        sort_keys = ['vsphere', 'name']
        all_dvs.sort(key=itemgetter(*sort_keys))
        for dvs in all_dvs:
            count += 1
            print(tpl.format(**dvs))

    # -------------------------------------------------------------------------
    def print_dv_portgroups(self):
        """Print on STDOUT all information about Distributed Virtual Port Groups."""
        all_dvpgs = []

        print()
        title = _('Distributed Virtual Port Groups')
        print(self.colored(title, 'cyan'))
        print(self.colored('=' * len(title), 'cyan'))

        for vsphere_name in self.vsphere:
            for name in self.vsphere[vsphere_name].dv_portgroups.keys():
                this_dvpg = self.vsphere[vsphere_name].dv_portgroups[name]
                dvs_name = '~'
                dvs_uuid = this_dvpg.dvs_uuid
                if dvs_uuid in self.vsphere[vsphere_name].dvs:
                    dvs_name = self.vsphere[vsphere_name].dvs[dvs_uuid].name
                network = '~'
                if this_dvpg.network:
                    network = str(this_dvpg.network)
                uplink = _('No')
                if this_dvpg.uplink:
                    uplink = _('Yes')
                accessible = 'No'
                if this_dvpg.accessible:
                    accessible = _('Yes')

                dvpg = {
                    'vsphere': vsphere_name,
                    'name': name,
                    'dvs': dvs_name,
                    'network': network,
                    'accessible': accessible,
                    'num_ports': '{:,}'.format(this_dvpg.num_ports),
                    'type': this_dvpg.type,
                    'uplink': uplink,
                    'description': this_dvpg.description,
                }
                all_dvpgs.append(dvpg)

        if len(all_dvpgs):
            self._print_dv_portgroups(all_dvpgs)
            return

        print()
        print(_('No Distributed Virtual Port Groups found.'))

    # -------------------------------------------------------------------------
    def _print_dv_portgroups(self, all_dvpgs):

        labels = {
            'vsphere': 'VSPhere',
            'name': _('Name'),
            'dvs': 'DV Switch',
            'network': _('Network'),
            'accessible': _('Accessible'),
            'num_ports': _('Ports'),
            'type': _('Type'),
            'uplink': _('Uplink'),
            'description': _('Description'),
        }
        label_list = (
            'name', 'vsphere', 'dvs', 'network', 'accessible', 'type',
            'num_ports', 'uplink', 'description'
        )

        str_lengths = {}
        for label in labels:
            str_lengths[label] = len(labels[label])

        max_len = 0
        count = 0
        for dvpg in all_dvpgs:
            for label in labels.keys():
                val = dvpg[label]
                if val is None:
                    val = '-'
                    dvpg[label] = val
                if len(val) > str_lengths[label]:
                    str_lengths[label] = len(val)

        for label in labels.keys():
            if max_len:
                max_len += 2
            max_len += str_lengths[label]

        if self.verbose > 1:
            LOG.debug('Label length:\n' + pp(str_lengths))
            LOG.debug('Max line length: {} chars'.format(max_len))

        tpl = ''
        for label in label_list:
            if tpl != '':
                tpl += '  '
            if label in ('num_ports',):
                tpl += '{{{la}:>{le}}}'.format(la=label, le=str_lengths[label])
            else:
                tpl += '{{{la}:<{le}}}'.format(la=label, le=str_lengths[label])
        if self.verbose > 1:
            LOG.debug(_('Line template: {}').format(tpl))

        if not self.quiet:
            print()
            print(tpl.format(**labels))
            print('-' * max_len)

        for dvpg in all_dvpgs:
            count += 1
            print(tpl.format(**dvpg))

    # -------------------------------------------------------------------------
    def print_networks(self):
        """Print on STDOUT all information about Virtual Networks."""
        all_networks = []

        print()
        title = _('Virtual Networks')
        print(self.colored(title, 'cyan'))
        print(self.colored('=' * len(title), 'cyan'))

        for vsphere_name in self.vsphere:
            for name in self.vsphere[vsphere_name].networks.keys():
                this_network = self.vsphere[vsphere_name].networks[name]
                network = '~'
                if this_network.network:
                    network = str(this_network.network)
                accessible = 'No'
                if this_network.accessible:
                    accessible = _('Yes')

                net = {
                    'vsphere': vsphere_name,
                    'name': name,
                    'network': network,
                    'accessible': accessible,
                }
                all_networks.append(net)

        if len(all_networks):
            self._print_networks(all_networks)
            return

        print()
        print(_('No Virtual Networks found.'))

    # -------------------------------------------------------------------------
    def _print_networks(self, all_networks):

        labels = {
            'vsphere': 'VSPhere',
            'name': _('Name'),
            'network': _('Network'),
            'accessible': _('Accessible'),
        }
        label_list = ('name', 'vsphere', 'network', 'accessible')

        str_lengths = {}
        for label in labels:
            str_lengths[label] = len(labels[label])

        max_len = 0
        count = 0
        for net in all_networks:
            for label in labels.keys():
                val = net[label]
                if val is None:
                    val = '-'
                    net[label] = val
                if len(val) > str_lengths[label]:
                    str_lengths[label] = len(val)

        for label in labels.keys():
            if max_len:
                max_len += 2
            max_len += str_lengths[label]

        if self.verbose > 1:
            LOG.debug('Label length:\n' + pp(str_lengths))
            LOG.debug('Max line length: {} chars'.format(max_len))

        tpl = ''
        for label in label_list:
            if tpl != '':
                tpl += '  '
            tpl += '{{{la}:<{le}}}'.format(la=label, le=str_lengths[label])
        if self.verbose > 1:
            LOG.debug(_('Line template: {}').format(tpl))

        if not self.quiet:
            print()
            print(tpl.format(**labels))
            print('-' * max_len)

        for net in all_networks:
            count += 1
            print(tpl.format(**net))


# =============================================================================
if __name__ == '__main__':

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
