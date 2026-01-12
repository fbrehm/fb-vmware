#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@summary: Search a datastore for vdisk of a given size in a VMware vSphere.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2026 by Frank Brehm, Berlin
"""
from __future__ import absolute_import, print_function

# Standard modules
import locale
import logging
import pathlib
import sys

# from fb_tools.argparse_actions import RegexOptionAction
# from fb_tools.common import pp
# from fb_tools.spinner import Spinner
from fb_tools.xlate import format_list

# Own modules
from . import BaseVmwareApplication
# from . import VmwareAppError
from .. import __version__ as GLOBAL_VERSION
from ..argparse_actions import NonNegativeIntegerOptionAction
# from ..datastore import VsphereDatastore
from ..datastore import VsphereDatastoreDict
from ..ds_cluster import VsphereDsCluster
from ..ds_cluster import VsphereDsClusterDict
# from ..errors import VSphereExpectedError
from ..xlate import XLATOR

__version__ = "0.3.1"
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext
ngettext = XLATOR.ngettext


# =============================================================================
class SearchStorageApp(BaseVmwareApplication):
    """Class for the application object."""

    show_simulate_option = False
    default_all_vspheres = False

    valid_storage_types = []
    for storage_type in VsphereDsCluster.valid_storage_types:
        valid_storage_types.append(storage_type.lower())
    valid_storage_types.append("any")

    # -------------------------------------------------------------------------
    def __init__(
        self,
        appname=None,
        verbose=0,
        version=GLOBAL_VERSION,
        base_dir=None,
        initialized=False,
        usage=None,
        description=None,
        argparse_epilog=None,
        argparse_prefix_chars="-",
        env_prefix=None,
    ):
        """Initialize a GetStorageListApp object."""
        desc = _(
            "Searches for a storage cluster or a datastore for a planned volume of a given size."
        )

        self.datastores = VsphereDatastoreDict()
        self.ds_clusters = VsphereDsClusterDict()

        self.cur_vsphere = None
        self.dc = None
        self.cluster = None

        self.disk_size_gb = None
        self.storage_type = None

        super(SearchStorageApp, self).__init__(
            appname=appname,
            verbose=verbose,
            version=version,
            base_dir=base_dir,
            description=desc,
            initialized=False,
        )

        self.initialized = True

    # -------------------------------------------------------------------------
    def init_arg_parser(self):
        """Public available method to initiate the argument parser."""
        search_options = self.arg_parser.add_argument_group(_("Search options"))

        search_options.add_argument(
            "-S",
            "--size",
            dest="size",
            type=int,
            metavar=_("GBYTE"),
            action=NonNegativeIntegerOptionAction,
            may_zero=False,
            help=_(
                "The size of the virtual disk, for which a storage location should be searched."
            ),
        )

        typelist = format_list(self.valid_storage_types, do_repr=True)
        help_msg = _(
            "The required storage type of the resulting volume. Valid types are {types}."
        ).format(types=typelist, deflt="any")
        search_options.add_argument(
            "-T",
            "--type",
            "--storage-type",
            metavar=_("TYPE"),
            choices=self.valid_storage_types,
            help=help_msg,
        )

        search_options.add_argument(
            "--vs",
            "--vsphere",
            dest="req_vsphere",
            help=_(
                "The vSphere name from configuration, in which the storage should be searched."
            ),
        )

        search_options.add_argument(
            "-D",
            "--dc",
            "--datacenter",
            metavar=_("DATACENTER"),
            dest="dc",
            help=_("The virtual datacenter in vSphere, in which the storage should be searched."),
        )

        search_options.add_argument(
            "--cluster",
            metavar=_("CLUSTER"),
            dest="cluster",
            help=_(
                "The computing cluster, which should be connected with the datastore cluster "
                "or datastore in result."
            ),
        )

        super(SearchStorageApp, self).init_arg_parser()

    # -------------------------------------------------------------------------
    def add_vsphere_argument(self):
        """Add a commandline option for selecting the vSphere to use."""
        pass

    # -------------------------------------------------------------------------
    def perform_arg_parser(self):
        """Evaluate command line parameters."""
        super(SearchStorageApp, self).perform_arg_parser()

        if getattr(self.args, "size", None) is not None:
            self.disk_size_gb = self.args.size

        if self.args.req_vsphere:
            vsphere = self.args.req_vsphere
            self.args.req_vsphere = [vsphere]
            LOG.info(_("Selected vSphere: {}").format(self.colored(vsphere, "CYAN")))

        if getattr(self.args, "dc", None) is not None and self.args.dc.strip() != "":
            self.dc = self.args.dc.strip()

        if getattr(self.args, "cluster", None) is not None and self.args.cluster.strip() != "":
            self.cluster = self.args.cluster.strip()

    # -------------------------------------------------------------------------
    def pre_run(self):
        """Execute some actions before the main routine."""
        if self.disk_size_gb is None:
            self.disk_size_gb = self.prompt_for_disk_size()

        vs_name = self.select_vsphere()
        self.do_vspheres = [vs_name]

        super(SearchStorageApp, self).pre_run()
        self.cur_vsphere = self.vsphere[vs_name]

        dc_name = self.select_datacenter(vs_name, self.dc)
        if dc_name is None:
            self.exit(1)

        LOG.info(
            _(
                "Searching a storage location in vSphere {vs}, virtual datacenter {dc} "
                "for a disk of {sz}."
            ).format(
                vs=self.colored(vs_name, "CYAN"),
                dc=self.colored(dc_name, "CYAN"),
                sz=self.colored(str(self.disk_size_gb) + " GiByte", "CYAN"),
            )
        )

    # -------------------------------------------------------------------------
    def _run(self):

        LOG.debug(_("Starting {a!r}, version {v!r} ...").format(a=self.appname, v=self.version))

        ret = 0
        try:
            LOG.info("And now - it starts ...")
        finally:
            self.cleaning_up()

        self.exit(ret)

    # -------------------------------------------------------------------------
    def post_run(self):
        """Execute some actions after the main routine."""
        super(SearchStorageApp, self).post_run()

        self.cur_vsphere = None


# =============================================================================
def main():
    """Entrypoint for search-vsphere-storage."""
    my_path = pathlib.Path(__file__)
    appname = my_path.name

    locale.setlocale(locale.LC_ALL, "")

    app = SearchStorageApp(appname=appname)
    app.initialized = True

    if app.verbose > 2:
        print(_("{c}-Object:\n{a}").format(c=app.__class__.__name__, a=app), file=sys.stderr)

    try:
        app()
    except KeyboardInterrupt:
        print("\n" + app.colored(_("User interrupt."), "YELLOW"))
        sys.exit(5)

    return 0


# =============================================================================
if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
