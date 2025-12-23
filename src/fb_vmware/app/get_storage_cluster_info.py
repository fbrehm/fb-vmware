#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Print all available information about a given storaage cluster.

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

# Third party modules
from babel.numbers import format_decimal

from fb_tools.common import pp
from fb_tools.spinner import Spinner
from fb_tools.xlate import format_list

from rich.table import Table

# Own modules
from . import BaseVmwareApplication
from . import VmwareAppError
from .. import __version__ as GLOBAL_VERSION
from ..errors import VSphereExpectedError
from ..xlate import XLATOR

__version__ = "1.0.2"
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext
ngettext = XLATOR.ngettext


# =============================================================================
class GetStorageClusterInfoAppError(VmwareAppError):
    """Base exception class for all exceptions in this application."""

    pass


# =============================================================================
class GetStorageClusterInfoApp(BaseVmwareApplication):
    """Class for the application objects."""

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
        """Initialize the GetStorageClusterInfoApp object."""
        desc = _(
            "Tries to get information about the given datastore cluster in "
            "VMware vSphere and print it out."
        )

        self.ds_cluster_names = []

        super(GetStorageClusterInfoApp, self).__init__(
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
        """Initiate the argument parser."""
        self.arg_parser.add_argument(
            "clusters",
            metavar="CLUSTER",
            type=str,
            nargs="+",
            help=_("Names of the datastore clusters to get information."),
        )

        super(GetStorageClusterInfoApp, self).init_arg_parser()

    # -------------------------------------------------------------------------
    def perform_arg_parser(self):
        """Evaluate the command line parameters. Maybe overridden."""
        super(GetStorageClusterInfoApp, self).perform_arg_parser()

        for cluster in self.args.clusters:
            self.ds_cluster_names.append(cluster)

    # -------------------------------------------------------------------------
    def _run(self):

        LOG.debug(_("Starting {a!r}, version {v!r} ...").format(a=self.appname, v=self.version))

        ret = 99
        try:
            ret = self.show_ds_clusters()
        finally:
            self.cleaning_up()

        self.exit(ret)

    # -------------------------------------------------------------------------
    def show_ds_clusters(self):
        """Show all datastore clusters."""
        ret = 0

        try:
            for vsphere_name in self.vsphere:
                vsphere = self.vsphere[vsphere_name]
                vsphere.get_datacenters()

        except VSphereExpectedError as e:
            LOG.error(str(e))
            self.exit(8)

        for cluster_name in sorted(self.ds_cluster_names, key=str.lower):
            if not self.show_ds_cluster(cluster_name):
                ret = 1

        return ret

    # -------------------------------------------------------------------------
    def show_ds_cluster(self, cluster_name):
        """Show a particular datastorecluster on STDOUT."""
        print()
        msg_tpl = _("Getting data of datastora cluster {} ... ")
        if self.verbose:
            msg = msg_tpl.format(self.colored(cluster_name, "CYAN"))
            print(msg)
            ds_cluster = self._get_ds_cluster_obj(cluster_name)
        else:
            msg_len = len(msg_tpl.format(cluster_name))
            spin_prompt = msg_tpl.format(self.colored(cluster_name, "CYAN"))
            spinner_name = self.get_random_spinner_name()
            with Spinner(spin_prompt, spinner_name):
                ds_cluster = self._get_ds_cluster_obj(cluster_name)
            sys.stdout.write(" " * msg_len)
            sys.stdout.write("\r")
            sys.stdout.flush()

        print("{}: ".format(cluster_name), end="")
        if not ds_cluster:
            print(self.colored(_("NOT FOUND"), "RED"))
            return False

        print("{ok}".format(ok=self.colored("OK", "GREEN")))
        print()

        dsc_table = Table(title=ds_cluster.name, title_style="bold cyan", box=None)
        dsc_table.add_column(highlight=True, style="bold", no_wrap=True)
        dsc_table.add_column()

        info_table = Table(box=None, show_header=False, show_footer=False)
        info_table.add_column(highlight=True, no_wrap=True)
        info_table.add_column()
        info_table.add_row("vSphere:", ds_cluster.vsphere)
        info_table.add_row("Datacenter:", ds_cluster.dc_name)
        info_table.add_row(
            _("Connected computing clusters") + ":",
            format_list(sorted(ds_cluster.compute_clusters)),
        )

        dsc_table.add_row(_("General"), info_table)
        dsc_table.add_row("", "")

        usage_pc_out = "- %"
        used = ds_cluster.capacity_gb - ds_cluster.free_space_gb
        if ds_cluster.capacity_gb:
            used_pc = used / ds_cluster.capacity_gb
            usage_pc_out = format_decimal(used_pc, format="0.0 %")

        cap_table = Table(box=None, show_footer=True)
        cap_table.add_column(header=_("Datastore"), footer=_("Datastore cluster total"))
        cap_table.add_column(
            header=_("Capacity in GB"),
            footer=format_decimal(ds_cluster.capacity_gb, format="#,##0"),
            justify="right",
        )
        cap_table.add_column(
            header=_("Calculated usage in GB"),
            footer=format_decimal(used, format="#,##0"),
            justify="right",
        )
        cap_table.add_column(header=_("Usage in percent"), footer=usage_pc_out, justify="right")
        cap_table.add_column(
            header=_("Free space in GB"),
            footer=format_decimal(ds_cluster.free_space_gb, format="#,##0"),
            justify="right",
        )
        for ds_name in sorted(ds_cluster.datastores.keys(), key=str.lower):
            ds = ds_cluster.datastores[ds_name]
            ds_used = ds.capacity_gb - ds.free_space_gb
            ds_used_pc = "- %"
            if ds.capacity_gb:
                ds_used_pc = format_decimal((ds_used / ds.capacity_gb), format="0.0 %")
            cap_table.add_row(
                ds_name,
                format_decimal(ds.capacity_gb, format="#,##0"),
                format_decimal(ds_used, format="#,##0"),
                ds_used_pc,
                format_decimal(ds.free_space_gb, format="#,##0"),
            )

        dsc_table.add_row(_("Capacity"), cap_table)
        dsc_table.add_row("", "")

        hosts_table = Table(box=None, show_header=False, show_footer=False)
        hosts_table.add_column()
        for host in sorted(ds_cluster.hosts, key=str.lower):
            hosts_table.add_row("* " + host)

        dsc_table.add_row(_("Connected hosts"), hosts_table)
        dsc_table.add_row("", "")

        self.rich_console.print(dsc_table)

    # -------------------------------------------------------------------------
    def _get_ds_cluster_obj(self, cluster_name):

        if self.verbose > 1:
            LOG.debug(
                _("Pulling full data of datastore cluster {} ...").format(
                    self.colored(cluster_name, "CYAN")
                )
            )

        ds_cluster = None

        for vsphere_name in self.vsphere:
            vsphere = self.vsphere[vsphere_name]
            LOG.debug(
                _("Searching for datastore cluster {dsc} in vSphere {vs} ...").format(
                    dsc=self.colored(cluster_name, "CYAN"), vs=self.colored(vsphere_name, "CYAN")
                )
            )

            ds_cluster = vsphere.get_ds_cluster(
                cluster_name, vsphere_name=vsphere_name, no_error=True, detailled=True
            )
            if not ds_cluster:
                continue

            break

        if self.verbose > 2:
            LOG.debug(
                "Got data of datastore cluster {}:\n".format(cluster_name)
                + pp(ds_cluster.as_dict())
            )

        return ds_cluster


# =============================================================================
def main():
    """Entrypoint for get-vsphere-vm-info."""
    my_path = pathlib.Path(__file__)
    appname = my_path.name

    locale.setlocale(locale.LC_ALL, "")

    app = GetStorageClusterInfoApp(appname=appname)
    app.initialized = True

    if app.verbose > 2:
        print(_("{c}-Object:\n{a}").format(c=app.__class__.__name__, a=app), file=sys.stderr)

    try:
        app()
    except KeyboardInterrupt:
        print("\n" + app.colored(_("User interrupt."), "YELLOW"))
        sys.exit(5)

    sys.exit(0)


# =============================================================================
if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
