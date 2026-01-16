#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Print a list of all physical hosts in a VMware vSphere.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import absolute_import, print_function

# Standard modules
import locale
import logging
import pathlib
import re
import sys
from operator import itemgetter

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
from ..errors import VSphereExpectedError
from ..host import VsphereHost
from ..xlate import XLATOR

__version__ = "1.5.4"
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext
ngettext = XLATOR.ngettext


# =============================================================================
class GetVmHostsAppError(VmwareAppError):
    """Base exception class for all exceptions in this application."""

    pass


# =============================================================================
class GetHostsListApplication(BaseVmwareApplication):
    """Class for the application object."""

    default_host_pattern = r".*"
    avail_sort_keys = ("name", "vsphere", "cluster", "vendor", "model", "os_version")
    default_sort_keys = ["name", "vsphere"]

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
        """Initialize a GetHostsListApplication object."""
        desc = _(
            "Tries to get a list of all physical hosts in VMware vSphere and print it out."
        )

        self._host_pattern = self.default_host_pattern
        self.sort_keys = self.default_sort_keys

        self.hosts = []

        super(GetHostsListApplication, self).__init__(
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
    def host_pattern(self):
        """Return the regex search pattern for filtering the host list."""
        return self._host_pattern

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transform the elements of the object into a dict.

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """
        res = super(GetHostsListApplication, self).as_dict(short=short)
        res["host_pattern"] = self.host_pattern
        res["default_host_pattern"] = self.default_host_pattern

        return res

    # -------------------------------------------------------------------------
    def init_arg_parser(self):
        """Public available method to initiate the argument parser."""
        filter_group = self.arg_parser.add_argument_group(_("Filter options"))

        filter_group.add_argument(
            "-p",
            "--pattern",
            "--search-pattern",
            dest="host_pattern",
            metavar="REGEX",
            action=RegexOptionAction,
            topic=_("for names of hosts"),
            re_options=re.IGNORECASE,
            help=_(
                "A regular expression to filter the output list of hosts by their name "
                "(Default: {!r})."
            ).format(self.default_host_pattern),
        )

        online_filter = filter_group.add_mutually_exclusive_group()
        online_filter.add_argument(
            "--on",
            "--online",
            action="store_true",
            dest="online",
            help=_("Filter output for online hosts."),
        )
        online_filter.add_argument(
            "--off",
            "--offline",
            action="store_true",
            dest="offline",
            help=_("Filter output for offline hosts and templates."),
        )

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

        super(GetHostsListApplication, self).init_arg_parser()

    # -------------------------------------------------------------------------
    def perform_arg_parser(self):
        """Evaluate command line parameters."""
        super(GetHostsListApplication, self).perform_arg_parser()

        if self.args.host_pattern:
            try:
                re_name = re.compile(self.args.host_pattern, re.IGNORECASE)
                LOG.debug(_("Regular expression for filtering: {!r}").format(re_name.pattern))
                self._host_pattern = self.args.host_pattern
            except Exception as e:
                msg = _("Got a {c} for pattern {p!r}: {e}").format(
                    c=e.__class__.__name__, p=self.args.host_pattern, e=e
                )
                LOG.error(msg)

        if self.args.sort_keys:
            self.sort_keys = self.args.sort_keys

    # -------------------------------------------------------------------------
    def _run(self):

        LOG.debug(_("Starting {a!r}, version {v!r} ...").format(a=self.appname, v=self.version))

        ret = 0
        try:
            ret = self.get_all_hosts()
        except VSphereExpectedError as e:
            LOG.error(str(e))
            self.exit(6)
        finally:
            self.cleaning_up()

        self.exit(ret)

    # -------------------------------------------------------------------------
    def get_all_hosts(self):
        """Collect all physical VMware hosts."""
        ret = 0
        all_hosts = []

        if self.verbose:
            for vsphere_name in self.vsphere:
                all_hosts += self.get_hosts(vsphere_name)
        elif not self.quiet:
            spin_prompt = _("Getting all vSphere hosts ...") + " "
            spinner_name = self.get_random_spinner_name()
            with Spinner(spin_prompt, spinner_name):
                for vsphere_name in self.vsphere:
                    all_hosts += self.get_hosts(vsphere_name)
            sys.stdout.write(" " * len(spin_prompt))
            sys.stdout.write("\r")
            sys.stdout.flush()

        first = True
        out_hosts = []

        for host in all_hosts:
            if self.verbose > 1 and first:
                LOG.debug(_("First found host:") + "\n" + pp(host.as_dict()))
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
        """Return a dict with host properties as a summary for the given host."""
        summary = {}

        summary["vsphere"] = host.vsphere
        summary["dc"] = host.dc_name
        summary["cluster"] = host.cluster_name
        summary["name"] = host.name
        summary["connection_state"] = host.connection_state
        cpu_cores = "-"
        if host.cpu_cores:
            cpu_cores = host.cpu_cores
        cpu_threads = "-"
        if host.cpu_threads:
            cpu_threads = host.cpu_threads
        summary["cpus"] = "{co}/{thr}".format(co=cpu_cores, thr=cpu_threads)
        summary["memory_gb"] = host.memory_gb
        summary["vendor"] = host.vendor
        summary["model"] = host.model
        summary["maintenance"] = host.maintenance
        summary["online"] = host.online
        summary["no_portgroups"] = str(len(host.portgroups))
        summary["power_state"] = host.power_state
        summary["standby"] = host.standby
        summary["os_name"] = host.product.name
        summary["os_version"] = host.product.os_version
        summary["quarantaine"] = host.quarantaine

        return summary

    # -------------------------------------------------------------------------
    def print_hosts(self, hosts):
        """Print on STDOUT all information about all hosts in a human readable format."""
        hosts.sort(key=itemgetter(*self.sort_keys))

        show_header = True
        table_title = _("All physical hosts") + "\n"
        box_style = box.ROUNDED
        if self.quiet:
            show_header = False
            table_title = None
            box_style = None

        if self.quiet:
            caption = None
        else:
            count = len(hosts)
            if count:
                caption = "\n" + ngettext(
                    "Found one VMware host.",
                    "Found {} VMware hosts.",
                    count,
                ).format(count)
            else:
                caption = "\n" + _("Found no VMware hosts.")

        table = Table(
            title=table_title,
            title_style="bold cyan",
            caption=caption,
            caption_style="default on default",
            caption_justify="left",
            box=box_style,
            show_header=show_header,
            show_footer=False,
        )

        table.add_column(header=_("Host"))
        table.add_column(header=_("vSphere"))
        table.add_column(header=_("Data Center"))
        table.add_column(header=_("Cluster"))
        table.add_column(header=_("Vendor"))
        table.add_column(header=_("Model"))
        table.add_column(header=_("OS Name"))
        table.add_column(header=_("OS Version"))
        table.add_column(header=_("CPU cores/threads"), justify="right")
        table.add_column(header=_("Memory in GiB"), justify="right")
        table.add_column(header=_("Power State"))
        table.add_column(header=_("Connect state"))
        table.add_column(header=_("StandBy state"), justify="center")
        table.add_column(header=_("Maintenance"), justify="center")

        for host in hosts:
            row = []

            row.append(host["name"])
            row.append(host["vsphere"])
            row.append(host["dc"])
            row.append(host["cluster"])
            row.append(host["vendor"])
            row.append(host["model"])
            row.append(host["os_name"])
            row.append(host["os_version"])
            row.append(host["cpus"])
            row.append(format_decimal(host["memory_gb"], format="#,##0"))

            power_state = host["power_state"]
            if power_state in VsphereHost.power_state_label:
                power_state = VsphereHost.power_state_label[power_state]
            p_state = Text(power_state)
            if host["power_state"].lower() == "poweredon":
                p_state.stylize("bold green")
            elif host["power_state"].lower() == "poweredoff":
                p_state.stylize("bold red")
            elif host["power_state"].lower() == "standby":
                p_state.stylize("bold blue")
            else:
                p_state.stylize("bold magenta")
            row.append(p_state)

            connection_state = host["connection_state"]
            if connection_state in VsphereHost.connect_state_label:
                connection_state = VsphereHost.connect_state_label[connection_state]
            c_state = Text(connection_state)
            if host["connection_state"].lower() == "connected":
                c_state.stylize("bold green")
            elif host["connection_state"].lower() == "disconnected":
                c_state.stylize("bold red")
            else:
                c_state.stylize("bold magenta")
            row.append(c_state)

            standby = host["standby"]
            if standby == "none":
                standby = "~"
            if standby in VsphereHost.standby_mode_label:
                standby = VsphereHost.standby_mode_label[standby]
            row.append(standby)

            m_state = Text(_("No"), style="bold green")
            if host["maintenance"]:
                m_state = Text(_("Yes"), style="bold yellow")
            row.append(m_state)

            table.add_row(*row)

        self.rich_console.print(table)

        if not self.quiet:
            print()

    # -------------------------------------------------------------------------
    def get_hosts(self, vsphere_name):
        """Get all host of all physical hosts in a VMware vSphere."""
        hosts = []

        vsphere = self.vsphere[vsphere_name]
        # vsphere.get_datacenter()

        re_name = None
        if self.host_pattern is not None:
            re_name = re.compile(self.host_pattern, re.IGNORECASE)

        vsphere.get_hosts(re_name=re_name, vsphere_name=vsphere_name)

        for host_name in sorted(vsphere.hosts.keys()):
            host = vsphere.hosts[host_name]
            hosts.append(host)

        return hosts


# =============================================================================
def main():
    """Entrypoint for get-vsphere-host-list."""
    my_path = pathlib.Path(__file__)
    appname = my_path.name

    locale.setlocale(locale.LC_ALL, "")

    app = GetHostsListApplication(appname=appname)
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
