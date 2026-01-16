#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Print a list of all resouce pools in a VMware vSphere.

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
from operator import attrgetter

# Third party modules
from babel.numbers import format_decimal

from fb_tools.common import pp
from fb_tools.spinner import Spinner
from fb_tools.xlate import format_list

from rich import box
from rich.table import Table
from rich.text import Text

# Own modules
from . import BaseVmwareApplication, VmwareAppError
from .. import __version__ as GLOBAL_VERSION
from ..errors import VSphereExpectedError
from ..xlate import XLATOR

__version__ = "1.1.0"
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext
ngettext = XLATOR.ngettext

# =============================================================================
class GetResPoolAppError(VmwareAppError):
    """Base exception class for all exceptions in this application."""

    pass


# =============================================================================
class GetResPoolListApplication(BaseVmwareApplication):
    """Class for the application object."""

    avail_sort_keys = ("name", "vsphere", "dc_name")
    default_sort_keys = ["vsphere", "dc_name", "name"]

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
        """Initialize a GetResPoolListApplication object."""
        desc = _(
            "Tries to get a list of all resource pools (a.k.a. computing resource and cluster "
            "computing resource) in VMware vSphere and print it out."
        )

        self.sort_keys = self.default_sort_keys

        super(GetResPoolListApplication, self).__init__(
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
        output_options = self.arg_parser.add_argument_group(_("Output options"))

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

        super(GetResPoolListApplication, self).init_arg_parser()

    # -------------------------------------------------------------------------
    def perform_arg_parser(self):
        """Evaluate command line parameters."""
        super(GetResPoolListApplication, self).perform_arg_parser()

        if self.args.sort_keys:
            self.sort_keys = self.args.sort_keys

    # -------------------------------------------------------------------------
    def _run(self):

        LOG.debug(_("Starting {a!r}, version {v!r} ...").format(a=self.appname, v=self.version))

        ret = 0
        try:
            ret = self.get_all_resource_pools()
        except VSphereExpectedError as e:
            LOG.error(str(e))
            self.exit(6)
        finally:
            self.cleaning_up()

        self.exit(ret)

    # -------------------------------------------------------------------------
    def get_all_resource_pools(self):
        """Collect all resource pools, a.k.a. (cluster) computing resources."""
        ret = 0
        all_rpools = []

        if self.verbose or self.quiet:
            for vsphere_name in self.vsphere:
                all_rpools += self.get_resource_pools(vsphere_name)
        else:
            spin_prompt = _("Getting all vSphere hosts ...") + " "
            spinner_name = self.get_random_spinner_name()
            with Spinner(spin_prompt, spinner_name):
                for vsphere_name in self.vsphere:
                    all_rpools += self.get_resource_pools(vsphere_name)
            sys.stdout.write(" " * len(spin_prompt))
            sys.stdout.write("\r")
            sys.stdout.flush()

        all_rpools.sort(key=attrgetter(*self.sort_keys))

        if len(all_rpools):
            out_list = []
            out = ""
            if self.verbose == 2:
                LOG.debug(_("First computing resource:") + "\n" + pp(all_rpools[0].as_dict()))
                for rpool in all_rpools:
                    out_list.append(
                        f" * Vsphere {rpool.vsphere:<10} - DC {rpool.dc_name:<12} - {rpool.name}")
                out = "\n".join(out_list)
            elif self.verbose > 2:
                for rpool in all_rpools:
                    out_list.append(rpool.as_dict())
                out = pp(out_list)
            if self.verbose >= 2:
                LOG.debug("All computing resources:\n{}".format(out))

            self.print_rpools(all_rpools)
        else:
            LOG.error(_("Did not found any resource pools or cluster resource pools."))
            if not self.quiet:
                print()
            ret = 3

        return ret

    # -------------------------------------------------------------------------
    def get_resource_pools(self, vsphere_name):
        """Get all host of all (cluster) computing resources in a VMware vSphere."""
        clusters = []

        vsphere = self.vsphere[vsphere_name]

        vsphere.get_clusters(vsphere_name=vsphere_name)

        for cluster in sorted(vsphere.clusters):
            clusters.append(cluster)

        return clusters

    # -------------------------------------------------------------------------
    def print_rpools(self, rpools):
        """Print on STDOUT all information about cluster) computing resources."""
        show_header = True
        show_footer = True
        table_title = _("All compute resources and cluster compute resources") + "\n"
        box_style = box.ROUNDED

        if self.quiet:
            show_header = False
            show_footer = False
            table_title = None
            box_style = None

        if self.quiet:
            caption = None
        else:
            count = len(rpools)
            if count:
                caption = "\n" + ngettext(
                    "Found one compute resource.",
                    "Found {} compute resources.",
                    count,
                ).format(count)
            else:
                caption = "\n" + _("Found no compute resources.")

        totals = self._get_totals(rpools)

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

        table.add_column(header=_("vSphere"), footer=_("Total:"))
        table.add_column(header=_("Data Center"), footer="")
        table.add_column(header=_("Name"), footer="")
        table.add_column(header=_("Cluster"), footer="")
        table.add_column(header=_("Pool name"), footer="")
        table.add_column(
            header=_("Hosts total"),
            justify="right",
            footer=self._prepare_number(totals["hosts_total"], warn_on_value1=True)
        )
        table.add_column(
            header=_("Hosts available"),
            justify="right",
            footer=self._prepare_number(
                totals["hosts_avail"],
                warn_on_value1=True,
                compare_val=totals["hosts_total"],
            ),
        )
        table.add_column(
            header=_("CPU cores"),
            justify="right",
            footer=self._prepare_number(totals["cpu_cores"])
        )
        table.add_column(
            header=_("CPU threads"),
            justify="right",
            footer=self._prepare_number(totals["cpu_threads"]),
        )
        table.add_column(
            header=_("Memory total"),
            justify="right",
            footer=self._prepare_number(totals["mem_total"]),
        )
        table.add_column(
            header=_("Memory available"),
            justify="right",
            footer=self._prepare_number(totals["mem_avail"], compare_val=totals["mem_total"]),
        )

        for rpool in rpools:
            row = []
            row.append(rpool.vsphere)
            row.append(rpool.dc_name)
            row.append(rpool.name)

            is_cluster = Text(_("Yes"), style="bold green")
            if rpool.standalone:
                is_cluster = Text(_("No"), style="green")

            row.append(is_cluster)
            row.append(rpool.base_resource_pool_name)
            row.append(self._prepare_number(rpool.hosts_total, warn_on_value1=True))
            row.append(self._prepare_number(
                    rpool.hosts_effective,
                    warn_on_value1=True,
                    compare_val=rpool.hosts_total,
                )
            )
            row.append(self._prepare_number(rpool.cpu_cores))
            row.append(self._prepare_number(rpool.cpu_threads))
            row.append(self._prepare_number(rpool.mem_mb_total))
            row.append(self._prepare_number(rpool.mem_mb_effective, compare_val=rpool.mem_mb_total))

            table.add_row(*row)

        self.rich_console.print(table)

        if not self.quiet:
            print()

    # -------------------------------------------------------------------------
    def _get_totals(self, rpools):

        totals = {
            "hosts_total": 0,
            "hosts_avail": 0,
            "cpu_cores": 0,
            "cpu_threads": 0,
            "mem_total": 0,
            "mem_avail": 0,
        }

        for rpool in rpools:
            totals["hosts_total"] += rpool.hosts_total
            totals["hosts_avail"] += rpool.hosts_effective
            totals["cpu_cores"] += rpool.cpu_cores
            totals["cpu_threads"] += rpool.cpu_threads
            totals["mem_total"] += rpool.mem_mb_total
            totals["mem_avail"] += rpool.mem_mb_effective

        return totals

    # -------------------------------------------------------------------------
    def _prepare_number(self, value, may_zero=False, warn_on_value1=False, compare_val=None):

        if value is None:
            return ""

        try:
            int_val = int(value)
        except ValueError:
            return value

        val_str = format_decimal(int_val, format="#,##0")
        if not may_zero and int_val == 0:
            val_str = Text(val_str, style="bold red")
        elif warn_on_value1 and int_val == 1:
            val_str = Text(val_str, style="bold yellow")
        elif compare_val is not None and int_val < compare_val:
            val_str = Text(val_str, style="bold yellow")

        return val_str


# =============================================================================
def main():
    """Entrypoint for get-vsphere-cluster-list."""
    my_path = pathlib.Path(__file__)
    appname = my_path.name

    locale.setlocale(locale.LC_ALL, "")

    app = GetResPoolListApplication(appname=appname)
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
