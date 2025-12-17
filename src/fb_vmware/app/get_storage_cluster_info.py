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
from fb_tools.common import pp
from fb_tools.spinner import Spinner

# Own modules
from . import BaseVmwareApplication
from . import VmwareAppError
from .. import __version__ as GLOBAL_VERSION
from ..errors import VSphereExpectedError
from ..xlate import XLATOR

__version__ = "0.1.0"
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
        super(GetStorageClusterInfoApp, self).init_arg_parser()

        self.arg_parser.add_argument(
            "clusters",
            metavar="CLUSTER",
            type=str,
            nargs="+",
            help=_("Names of the datastore clusters to get information."),
        )

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
                ds_cluster = self._get_vm_data(cluster_name)
            sys.stdout.write(" " * msg_len)
            sys.stdout.write("\r")
            sys.stdout.flush()

        print("{}: ".format(cluster_name), end="")
        if not ds_cluster:
            print(self.colored(_("NOT FOUND"), "RED"))
            return False

        print("{ok}".format(ok=self.colored("OK", "GREEN")))
        print()

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

        LOG.debug(
            "Got data of datastore cluster {}:\n".format(cluster_name) + pp(ds_cluster.as_dict())
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
