#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@summary: Print a list of all storage clusters in a VMware vSphere.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import absolute_import, print_function

# Standard modules
import locale
import logging
import pathlib
import sys
from operator import itemgetter

# Third party modules
from babel.numbers import format_decimal

# from fb_tools.argparse_actions import RegexOptionAction
from fb_tools.common import pp
from fb_tools.spinner import Spinner
from fb_tools.xlate import format_list

from rich import box
from rich.table import Table
from rich.text import Text

# Own modules
from . import BaseVmwareApplication
from . import VmwareAppError
from .. import __version__ as GLOBAL_VERSION
from ..ds_cluster import VsphereDsClusterDict
from ..errors import VSphereExpectedError
from ..xlate import XLATOR

__version__ = "1.5.0"
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
        "cluster_name",
        "vsphere_name",
        "capacity",
        "free_space",
        "usage",
        "usage_pc",
    )
    default_sort_keys = ["vsphere_name", "cluster_name"]

    show_simulate_option = False

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
        """Initialize a GetStorageClusterListApp object."""
        desc = _(
            "Tries to get a list of all datastore clusters in " "VMware vSphere and print it out."
        )

        self.st_clusters = []
        self._print_total = True
        self.totals = None
        self.sort_keys = self.default_sort_keys

        super(GetStorageClusterListApp, self).__init__(
            appname=appname,
            verbose=verbose,
            version=version,
            base_dir=base_dir,
            description=desc,
            initialized=False,
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
        res["print_total"] = self.print_total

        return res

    # -------------------------------------------------------------------------
    def init_arg_parser(self):
        """Public available method to initiate the argument parser."""
        output_options = self.arg_parser.add_argument_group(_("Output options"))

        output_options.add_argument(
            "-N",
            "--no-totals",
            action="store_true",
            dest="no_totals",
            help=_("Don't print the totals of all storage clusters."),
        )

        output_options.add_argument(
            "-S",
            "--sort",
            metavar="KEY",
            nargs="+",
            dest="sort_keys",
            choices=self.avail_sort_keys,
            help=_(
                "The keys for sorting the output. Available keys are: {avail}. "
                "The default sorting keys are: {default}."
            ).format(
                avail=format_list(self.avail_sort_keys, do_repr=True),
                default=format_list(self.default_sort_keys, do_repr=True),
            ),
        )

        super(GetStorageClusterListApp, self).init_arg_parser()

    # -------------------------------------------------------------------------
    def perform_arg_parser(self):
        """Evaluate command line parameters."""
        super(GetStorageClusterListApp, self).perform_arg_parser()

        if self.args.sort_keys:
            self.sort_keys = self.args.sort_keys

        if getattr(self.args, "no_totals", False):
            self._print_total = False

    # -------------------------------------------------------------------------
    def _run(self):

        LOG.debug(_("Starting {a!r}, version {v!r} ...").format(a=self.appname, v=self.version))

        ret = 0
        try:
            ret = self.get_all_storage_clusters()
        finally:
            self.cleaning_up()

        self.exit(ret)

    # -------------------------------------------------------------------------
    def get_datastore_clusters(self, vsphere_name):
        """Get all datastore clusters in a VMware vSphere."""
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
            spin_prompt = _("Getting all vSphere storage clusters ...")
            spinner_name = self.get_random_spinner_name()
            with Spinner(spin_prompt, spinner_name):
                _get_all_storage_clusters()
            sys.stdout.write(" " * len(spin_prompt))
            sys.stdout.write("\r")
            sys.stdout.flush()

        if self.verbose > 2:
            LOG.debug(_("Found datastore clusters:") + "\n" + pp(all_storage_clusters))

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
                cluster["is_total"] = False

                cluster["cluster_name"] = cluster_name

                cluster["vsphere_name"] = vsphere_name
                cluster["dc"] = cl.dc_name

                cluster["storage_type"] = cl.storage_type

                cluster["capacity"] = cl.capacity_gb
                cluster["capacity_gb"] = format_decimal(cl.capacity_gb, format="#,##0")
                total_capacity += cl.capacity_gb

                cluster["free_space"] = cl.free_space_gb
                cluster["free_space_gb"] = format_decimal(cl.free_space_gb, format="#,##0")
                total_free += cl.free_space_gb

                used = cl.capacity_gb - cl.free_space_gb
                cluster["usage"] = used
                cluster["usage_gb"] = format_decimal(used, format="#,##0")

                if cl.capacity_gb:
                    usage_pc = used / cl.capacity_gb
                    cluster["usage_pc"] = usage_pc
                    cluster["usage_pc_out"] = format_decimal(usage_pc, format="0.0 %")
                else:
                    cluster["usage_pc"] = None
                    cluster["usage_pc_out"] = "- %"

                cluster_list.append(cluster)

        total_used = total_capacity - total_free
        total_used_pc = None
        total_used_pc_out = "- %"
        if total_capacity:
            total_used_pc = total_used / total_capacity
            total_used_pc_out = format_decimal(total_used_pc, format="0.0 %")

        self.totals = {
            "cluster_name": _("Total"),
            "storage_type": "",
            "vsphere_name": "",
            "dc": "",
            "is_total": True,
            "capacity_gb": format_decimal(total_capacity, format="#,##0"),
            "free_space_gb": format_decimal(total_free, format="#,##0"),
            "usage_gb": format_decimal(total_used, format="#,##0"),
            "usage_pc_out": total_used_pc_out,
        }
        if not self.quiet:
            self.totals["cluster_name"] += ":"

        return cluster_list

    # -------------------------------------------------------------------------
    def print_clusters(self, clusters):
        """Print on STDOUT all information about all datastore clusters."""
        show_footer = False
        if self.print_total and not self.quiet:
            show_footer = True

        show_header = True
        table_title = _("All datastore clusters") + "\n"
        box_style = box.ROUNDED
        if self.quiet:
            show_header = False
            table_title = None
            box_style = None

        cluster_list = self._get_cluster_list(clusters)

        if self.sort_keys:
            LOG.debug("Sorting keys: " + pp(self.sort_keys))
            self.sort_keys.reverse()
            for key in self.sort_keys:
                if key in ("cluster_name", "vsphere_name"):
                    cluster_list.sort(key=itemgetter(key))
                else:
                    cluster_list.sort(key=itemgetter(key), reverse=True)

        if self.quiet:
            caption = None
        else:
            count = len(cluster_list)
            if count:
                caption = "\n" + ngettext(
                    "Found one VMware storage cluster.",
                    "Found {} VMware storage clusters.",
                    count,
                ).format(count)
            else:
                caption = "\n" + _("No VMware storage clusters found.")

        table = Table(
            title=table_title,
            title_style="bold cyan",
            caption=caption,
            caption_style="default on default",
            caption_justify="left",
            box=box_style,
            show_header=show_header,
            show_footer=show_footer,
        )

        table.add_column(header="Cluster", footer=_("Total"))
        table.add_column(header=_("Type"), justify="center", footer="")
        table.add_column(header=_("vSphere"), footer="")
        table.add_column(header=_("Data Center"), footer="")
        table.add_column(
            header=_("Capacity in GB"), footer=self.totals["capacity_gb"], justify="right"
        )
        table.add_column(
            header=_("Calculated usage in GB"), footer=self.totals["usage_gb"], justify="right"
        )
        table.add_column(
            header=_("Usage in percent"), footer=self.totals["usage_pc_out"], justify="right"
        )
        table.add_column(
            header=_("Free space in GB"), footer=self.totals["free_space_gb"], justify="right"
        )

        for cluster in cluster_list:
            used_pc_out = Text(cluster["usage_pc_out"])
            if cluster["usage_pc"] is None:
                used_pc_out.stylize("bold magenta")
            elif cluster["usage_pc"] >= 0.9:
                used_pc_out.stylize("bold red")
            elif cluster["usage_pc"] >= 0.8:
                used_pc_out.stylize("bold yellow")

            table.add_row(
                cluster["cluster_name"],
                cluster["storage_type"],
                cluster["vsphere_name"],
                cluster["dc"],
                cluster["capacity_gb"],
                cluster["usage_gb"],
                used_pc_out,
                cluster["free_space_gb"],
            )

        self.rich_console.print(table)

        if not self.quiet:
            print()


# =============================================================================
def main():
    """Entrypoint for get-vsphere-storage-cluster-list."""
    my_path = pathlib.Path(__file__)
    appname = my_path.name

    locale.setlocale(locale.LC_ALL, "")

    app = GetStorageClusterListApp(appname=appname)
    app.initialized = True

    if app.verbose > 2:
        print(_("{c}-Object:\n{a}").format(c=app.__class__.__name__, a=app), file=sys.stderr)

    app()

    sys.exit(0)


# =============================================================================
if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
