#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@summary: Print a list of all datastores (Storages) in a VMware vSphere.

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
from rich.console import Console
from rich.table import Table
from rich.text import Text

# Own modules
from . import BaseVmwareApplication
from . import VmwareAppError
from .. import __version__ as GLOBAL_VERSION
from ..datastore import VsphereDatastoreDict
from ..errors import VSphereExpectedError
from ..xlate import XLATOR

__version__ = "1.2.1"
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext
ngettext = XLATOR.ngettext


# =============================================================================
class GetVmStoragesAppError(VmwareAppError):
    """Base exception class for all exceptions in this application."""

    pass


# =============================================================================
class GetStorageListApp(BaseVmwareApplication):
    """Class for the application object."""

    avail_sort_keys = (
        "ds_name",
        "vsphere_name",
        "dc",
        "ecluster",
        "capacity",
        "free_space",
        "usage",
        "usage_pc",
    )
    default_sort_keys = ["vsphere_name", "dc", "ds_name"]

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
        desc = _("Tries to get a list of all datastores in VMware vSphere and print it out.")

        self.datastores = []
        self._print_total = True
        self._no_local = False
        self.totals = None
        self._detailled = False
        self.sort_keys = self.default_sort_keys

        super(GetStorageListApp, self).__init__(
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
    @property
    def no_local(self):
        """Don't print out local datastores on the ESX hosts."""
        return self._no_local

    # -------------------------------------------------------------------------
    @property
    def detailled(self):
        """Print out a more detailled info about the datastores."""
        return self._detailled

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transform the elements of the object into a dict.

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """
        res = super(GetStorageListApp, self).as_dict(short=short)
        res["detailled"] = self.detailled
        res["no_local"] = self.no_local
        res["print_total"] = self.print_total

        return res

    # -------------------------------------------------------------------------
    def init_arg_parser(self):
        """Public available method to initiate the argument parser."""
        super(GetStorageListApp, self).init_arg_parser()

        output_options = self.arg_parser.add_argument_group(_("Output options"))

        output_options.add_argument(
            "-L",
            "--no-local",
            action="store_true",
            dest="no_local",
            help=_("Don't print local datastores on the ESX hosts."),
        )

        output_options.add_argument(
            "-N",
            "--no-totals",
            action="store_true",
            dest="no_totals",
            help=_("Don't print the totals of all datastores."),
        )

        output_options.add_argument(
            "-D",
            "--detailled",
            action="store_true",
            dest="detailled",
            help=_(
                "Print out a more detailled info about the datastores, e.g. the number of "
                "connected hosts. Tooks significant more time to retrieve the data from vSphere."
            ),
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

    # -------------------------------------------------------------------------
    def perform_arg_parser(self):
        """Evaluate command line parameters."""
        super(GetStorageListApp, self).perform_arg_parser()

        if self.args.sort_keys:
            self.sort_keys = self.args.sort_keys

        if getattr(self.args, "no_totals", False):
            self._print_total = False

        if getattr(self.args, "no_local", False):
            self._no_local = True

        if getattr(self.args, "detailled", False):
            self._detailled = True

    # -------------------------------------------------------------------------
    def _run(self):

        LOG.debug(_("Starting {a!r}, version {v!r} ...").format(a=self.appname, v=self.version))

        ret = 0
        try:
            ret = self.get_all_datastores()
        finally:
            self.cleaning_up()

        self.exit(ret)

    # -------------------------------------------------------------------------
    def get_datastores(self, vsphere_name):
        """Get all datastore clusters in a VMware vSphere."""
        datastores = []

        vsphere = self.vsphere[vsphere_name]
        no_local_ds = False
        if self.no_local:
            no_local_ds = True
        try:
            vsphere.get_datastores(no_local_ds=no_local_ds, detailled=self.detailled)
        except VSphereExpectedError as e:
            LOG.error(str(e))
            self.exit(6)

        for datastore in vsphere.datastores:
            datastores.append(vsphere.datastores[datastore])

        return datastores

    # -------------------------------------------------------------------------
    def get_all_datastores(self):
        """Collect all datastores."""
        ret = 0
        all_datastores = {}

        # ----------
        def _get_all_datastores():

            for vsphere_name in self.vsphere:
                if vsphere_name not in all_datastores:
                    all_datastores[vsphere_name] = VsphereDatastoreDict()
                for datastore in self.get_datastores(vsphere_name):
                    all_datastores[vsphere_name].append(datastore)

        if self.verbose or self.quiet:
            _get_all_datastores()

        else:
            spin_prompt = _("Getting all vSphere datastores ...")
            spinner_name = self.get_random_spinner_name()
            with Spinner(spin_prompt, spinner_name):
                _get_all_datastores()
            sys.stdout.write(" " * len(spin_prompt))
            sys.stdout.write("\r")
            sys.stdout.flush()

        if self.verbose > 2:
            LOG.debug(_("Found datastores:") + "\n" + pp(all_datastores))

        self.print_datastores(all_datastores)

        return ret

    # -------------------------------------------------------------------------
    def _get_datastore_list(self, datastores):

        datastore_list = []

        total_capacity = 0.0
        total_free = 0.0

        first = True

        for vsphere_name in datastores.keys():
            for ds_name in datastores[vsphere_name].keys():

                ds = datastores[vsphere_name][ds_name]

                if self.verbose == 2 and first:
                    LOG.debug("First found datastore:\n" + pp(ds.as_dict()))
                    first = False

                datastore = {}
                datastore["is_total"] = False

                datastore["ds_name"] = ds_name

                if hasattr(ds, "hosts"):
                    datastore["hosts"] = str(len(ds.hosts))
                else:
                    datastore["hosts"] = "~"

                datastore["vsphere_name"] = vsphere_name
                datastore["dc"] = ds.dc_name
                datastore["cluster"] = "~"
                if ds.cluster:
                    datastore["cluster"] = ds.cluster

                datastore["capacity"] = ds.capacity_gb
                datastore["capacity_gb"] = format_decimal(ds.capacity_gb, format="#,##0")
                total_capacity += ds.capacity_gb

                datastore["free_space"] = ds.free_space_gb
                datastore["free_space_gb"] = format_decimal(ds.free_space_gb, format="#,##0")
                total_free += ds.free_space_gb

                used = ds.capacity_gb - ds.free_space_gb
                datastore["usage"] = used
                datastore["usage_gb"] = format_decimal(used, format="#,##0")

                if ds.capacity_gb:
                    usage_pc = used / ds.capacity_gb
                    datastore["usage_pc"] = usage_pc
                    datastore["usage_pc_out"] = format_decimal(usage_pc, format="0.0 %")
                else:
                    datastore["usage_pc"] = None
                    datastore["usage_pc_out"] = "- %"

                datastore_list.append(datastore)

        total_used = total_capacity - total_free
        total_used_pc = None
        total_used_pc_out = "- %"
        if total_capacity:
            total_used_pc = total_used / total_capacity
            total_used_pc_out = format_decimal(total_used_pc, format="0.0 %")

        self.totals = {
            "ds_name": _("Total"),
            "vsphere_name": "",
            "hosts": "",
            "dc": "",
            "cluster": "",
            "is_total": True,
            "capacity_gb": format_decimal(total_capacity, format="#,##0"),
            "free_space_gb": format_decimal(total_free, format="#,##0"),
            "usage_gb": format_decimal(total_used, format="#,##0"),
            "usage_pc_out": total_used_pc_out,
        }
        if not self.quiet:
            self.totals["ds_name"] += ":"

        return datastore_list

    # -------------------------------------------------------------------------
    def print_datastores(self, all_datastores):
        """Print on STDOUT all information about all datastore clusters."""
        show_footer = False
        if self.print_total and not self.quiet:
            show_footer = True

        show_header = True
        table_title = _("All datastores") + "\n"
        box_style = box.ROUNDED
        if self.quiet:
            show_header = False
            table_title = None
            box_style = None

        datastore_list = self._get_datastore_list(all_datastores)

        if self.sort_keys:
            LOG.debug("Sorting keys: " + pp(self.sort_keys))
            self.sort_keys.reverse()
            for key in self.sort_keys:
                if key in ("ds_name", "vsphere_name", "dc", "cluster"):
                    datastore_list.sort(key=itemgetter(key))
                else:
                    datastore_list.sort(key=itemgetter(key), reverse=True)

        if self.quiet:
            caption = None
        else:
            count = len(datastore_list)
            if count:
                caption = "\n" + ngettext(
                    "Found one VMware datastore.",
                    "Found {} VMware datastores.",
                    count,
                ).format(count)
            else:
                caption = "\n" + _("No VMware datastores found.")

        ds_table = Table(
            title=table_title,
            title_style="bold cyan",
            caption=caption,
            caption_style="default on default",
            caption_justify="left",
            box=box_style,
            show_header=show_header,
            show_footer=show_footer,
        )

        ds_table.add_column(header=_("Datastore"), footer=_("Total"))
        ds_table.add_column(header=_("vSphere"), footer="")
        ds_table.add_column(header=_("Data Center"), footer="")
        ds_table.add_column(header=_("Cluster"), footer="")
        ds_table.add_column(header=_("Connected Hosts"), footer="", justify="right")
        ds_table.add_column(
            header=_("Capacity in GB"), footer=self.totals["capacity_gb"], justify="right"
        )
        ds_table.add_column(
            header=_("Calculated usage in GB"), footer=self.totals["usage_gb"], justify="right"
        )
        ds_table.add_column(
            header=_("Usage in percent"), footer=self.totals["usage_pc_out"], justify="right"
        )
        ds_table.add_column(
            header=_("Free space in GB"), footer=self.totals["free_space_gb"], justify="right"
        )

        for datastore in datastore_list:
            used_pc_out = Text(datastore["usage_pc_out"])
            if datastore["usage_pc"] is None:
                used_pc_out.stylize("bold magenta")
            elif datastore["usage_pc"] >= 0.9:
                used_pc_out.stylize("bold red")
            elif datastore["usage_pc"] >= 0.8:
                used_pc_out.stylize("bold yellow")

            ds_table.add_row(
                datastore["ds_name"],
                datastore["vsphere_name"],
                datastore["dc"],
                datastore["cluster"],
                datastore["hosts"],
                datastore["capacity_gb"],
                datastore["usage_gb"],
                used_pc_out,
                datastore["free_space_gb"],
            )

        console = Console()
        console.print(ds_table)

        if not self.quiet:
            print()


# =============================================================================
def main():
    """Entrypoint for get-vsphere-storage-list."""
    my_path = pathlib.Path(__file__)
    appname = my_path.name

    locale.setlocale(locale.LC_ALL, "")

    app = GetStorageListApp(appname=appname)
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
