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

# from fb_tools.argparse_actions import RegexOptionAction
from fb_tools.common import pp
from fb_tools.spinner import Spinner
from fb_tools.xlate import format_list

# Own modules
from . import BaseVmwareApplication, VmwareAppError
from .. import __version__ as GLOBAL_VERSION
from ..network import VsphereNetworkDict
from ..errors import VSphereExpectedError
from ..xlate import XLATOR

__version__ = '1.2.1'
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

    avail_sort_keys = (
        'bla', 'blub')
    default_sort_keys = ['bla']

    # -------------------------------------------------------------------------
    def __init__(
        self, appname=None, verbose=0, version=GLOBAL_VERSION, base_dir=None,
            initialized=False, usage=None, description=None,
            argparse_epilog=None, argparse_prefix_chars='-', env_prefix=None):
        """Initialize a GetNetworkListApp object."""
        desc = _(
            'Tries to get a list of all networks in '
            'VMWare VSphere and print it out.')

        self.networks = []
        self.sort_keys = self.default_sort_keys

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

        ret = 0
        try:
            ret = self.get_all_networks()
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
    def get_all_networks(self):
        """Collect all networks."""
        ret = 0
        all_networks = {}

        # ----------
        def _get_all_networks():

            for vsphere_name in self.vsphere:
                if vsphere_name not in all_networks:
                    all_networks[vsphere_name] = VsphereNetworkDict()
                for network in self.get_networks(vsphere_name):
                    all_networks[vsphere_name].append(network)

        if self.verbose or self.quiet:
            _get_all_networks()

        else:
            spin_prompt = _('Getting all VSPhere networks ...')
            spinner_name = self.get_random_spinner_name()
            with Spinner(spin_prompt, spinner_name):
                _get_all_networks()
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
            if self.verbose > 3:
                # LOG.debug(_('Found networks:') + '\n' + pp(all_networks))
                for vsphere_name in self.vsphere:
                    networks[vsphere_name] = all_networks[vsphere_name].as_dict()
            else:
                for vsphere_name in self.vsphere:
                    networks[vsphere_name] = []
                    if len(all_networks[vsphere_name]):
                        key = all_networks[vsphere_name].keys()[0]
                        net = all_networks[vsphere_name][key]
                        networks[vsphere_name] = [net.as_dict()]

            msg = _('Found Virtual Networks:') + pp(networks)
            LOG.debug(msg)


        # self.print_clusters(all_storage_clusters)

        return ret


# =============================================================================
if __name__ == '__main__':

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
