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
import re
import sys
from operator import attrgetter

# Third party modules
from babel.numbers import format_decimal

from fb_tools.argparse_actions import RegexOptionAction
from fb_tools.common import pp
from fb_tools.spinner import Spinner
from fb_tools.xlate import format_list

from rich import box
from rich.table import Table
from rich.text import Text

# Own modules
from . import BaseVmwareApplication, VmwareAppError
from .. import __version__ as GLOBAL_VERSION
from ..cluster import VsphereCluster
from ..errors import VSphereExpectedError
from ..xlate import XLATOR

__version__ = "0.4.0"
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

        if self.verbose:
            for vsphere_name in self.vsphere:
                all_rpools += self.get_resource_pools(vsphere_name)
        elif not self.quiet:
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

        hosts_total = format_decimal(totals["hosts_total"], format="#,##0")
        if totals["hosts_total"] == 0:
            hosts_total = Text(hosts_total, style="bold red")
        elif totals["hosts_total"] == 1:
            hosts_total = Text(hosts_total, style="bold yellow")
        table.add_column(header=_("Hosts total"), justify="right", footer=hosts_total)

        hosts_avail = format_decimal(totals["hosts_avail"], format="#,##0")
        if totals["hosts_avail"] == 0:
            hosts_avail = Text(hosts_avail, style="bold red")
        elif totals["hosts_avail"] == 1 or totals["hosts_avail"] < totals["hosts_avail"]:
            hosts_avail = Text(hosts_avail, style="bold yellow")
        table.add_column(header=_("Hosts available"), justify="right", footer=hosts_avail)

        cpu_cores = format_decimal(totals["cpu_cores"], format="#,##0")
        if totals["cpu_cores"] == 0:
            cpu_cores = Text(cpu_cores, style="bold red")
        table.add_column(header=_("CPU cores"), justify="right", footer=cpu_cores)

        cpu_threads = format_decimal(totals["cpu_threads"], format="#,##0")
        if totals["cpu_threads"] == 0:
            cpu_threads = Text(cpu_threads, style="bold red")
        table.add_column(header=_("CPU threads"), justify="right", footer=cpu_threads)

        mem_total = format_decimal(totals["mem_total"], format="#,##0")
        if totals["mem_total"] == 0:
            mem_total = Text(mem_total, style="bold red")
        table.add_column(header=_("Memory total"), justify="right", footer=mem_total)

        mem_avail = format_decimal(totals["mem_avail"], format="#,##0")
        if totals["mem_avail"] == 0:
            mem_avail = Text(mem_avail, style="bold red")
        elif totals["mem_avail"] < totals["mem_avail"]:
            mem_avail = Text(mem_avail, style="bold yellow")
        table.add_column(header=_("Memory available"), justify="right", footer=mem_avail)

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

            hosts_total = format_decimal(rpool.hosts_total, format="#,##0")
            if rpool.hosts_total == 0:
                hosts_total = Text(hosts_total, style="bold red")
            elif rpool.hosts_total == 1:
                hosts_total = Text(hosts_total, style="bold yellow")
            row.append(hosts_total)

            hosts_avail = format_decimal(rpool.hosts_effective, format="#,##0")
            if rpool.hosts_effective == 0:
                hosts_avail = Text(hosts_avail, style="bold red")
            elif rpool.hosts_effective == 1 or rpool.hosts_effective < rpool.hosts_total:
                hosts_avail = Text(hosts_avail, style="bold yellow")
            row.append(hosts_avail)

            cpu_cores = format_decimal(rpool.cpu_cores, format="#,##0")
            if rpool.cpu_cores == 0:
                cpu_cores = Text(cpu_cores, style="bold red")
            row.append(cpu_cores)

            cpu_threads = format_decimal(rpool.cpu_threads, format="#,##0")
            if rpool.cpu_threads == 0:
                cpu_threads = Text(cpu_threads, style="bold red")
            row.append(cpu_threads)

            mem_total = format_decimal(rpool.mem_mb_total, format="#,##0")
            if rpool.mem_mb_total == 0:
                mem_total = Text(mem_total, style="bold red")
            row.append(mem_total)

            mem_avail = format_decimal(rpool.mem_mb_effective, format="#,##0")
            if rpool.hosts_effective == 0:
                mem_avail = Text(mem_avail, style="bold red")
            elif rpool.mem_mb_effective < rpool.mem_mb_total:
                mem_avail = Text(mem_avail, style="bold yellow")
            row.append(mem_avail)

            table.add_row(*row)

        self.rich_console.print(table)

        if not self.quiet:
            print()


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
