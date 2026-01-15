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
from fb_tools.common import pp
from fb_tools.spinner import Spinner
from fb_tools.xlate import format_list

# Own modules
from . import BaseVmwareApplication
from .. import __version__ as GLOBAL_VERSION
from ..argparse_actions import NonNegativeIntegerOptionAction
from ..datastore import VsphereDatastoreDict
from ..ds_cluster import VsphereDsCluster
from ..ds_cluster import VsphereDsClusterDict
from ..errors import VSphereExpectedError
from ..errors import VSphereNoDatastoreFoundError
from ..errors import VSphereNoDsClusterFoundError
from ..xlate import XLATOR

__version__ = "0.6.2"
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext
ngettext = XLATOR.ngettext
npgettext = XLATOR.npgettext
pgettext = XLATOR.pgettext


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

        self.vsphere_name = None
        self.cur_vsphere = None
        self.dc = None
        self.cluster = None
        self.cluster_type = None

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

        LOG.debug("Given arguments:\n" + pp(self.args))

        if getattr(self.args, "size", None) is not None:
            self.disk_size_gb = self.args.size

        if getattr(self.args, "type", None) is not None:
            self.storage_type = getattr(self.args, "type", None)

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

        storage_type = self.select_storage_type(self.storage_type)
        if storage_type is None:
            self.exit(1)
        self.storage_type = storage_type

        vs_name = self.select_vsphere()
        self.do_vspheres = [vs_name]

        super(SearchStorageApp, self).pre_run()
        self.vsphere_name = vs_name
        self.cur_vsphere = self.vsphere[vs_name]

        dc_name = self.select_datacenter(vs_name, self.dc)
        if dc_name is None:
            self.exit(1)
        self.dc = dc_name

        (cluster_name, cluster_type) = self.select_computing_cluster(
            vs_name=vs_name, dc_name=dc_name, cluster_name=self.cluster
        )
        if cluster_name[0] is None:
            self.exit(1)
        self.cluster = cluster_name
        self.cluster_type = cluster_type

        LOG.info(
            _(
                "Searching a storage location in vSphere {vs}, virtual datacenter {dc} "
                "connected with the {cl_type} {cl} "
                "for a disk of {sz} of type {st_type}."
            ).format(
                vs=self.colored(vs_name, "CYAN"),
                dc=self.colored(dc_name, "CYAN"),
                cl_type=self.cluster_type,
                cl=self.colored(self.cluster, "CYAN"),
                sz=self.colored(str(self.disk_size_gb) + " GiByte", "CYAN"),
                st_type=self.colored(storage_type, "CYAN"),
            )
        )

    # -------------------------------------------------------------------------
    def _run(self):

        LOG.debug(_("Starting {a!r}, version {v!r} ...").format(a=self.appname, v=self.version))

        ret = 0
        try:
            self.get_storages()
            self.search_for_space()
        finally:
            self.cleaning_up()

        self.exit(ret)

    # -------------------------------------------------------------------------
    def get_storages(self):
        """Retrieve all datastore clusters and storages in current vSphere and datacenter."""
        LOG.info(
            _("Collect all datastore clusters and storages in current vSphere and datacenter.")
        )

        self.get_datastore_clusters()
        len_ds_clusters = len(self.ds_clusters)
        if len_ds_clusters:
            one = pgettext("found_ds_cluster", "one")
            msg = ngettext(
                "Found total {one} datastore cluster in vSphere {vs}, datacenter {dc}.",
                "Found total {nr} datastore clusters in vSphere {vs}, datacenter {dc}.",
                len_ds_clusters,
            )
            msg = msg.format(
                one=self.colored(one, "CYAN"),
                nr=self.colored(str(len_ds_clusters), "CYAN"),
                vs=self.colored(self.vsphere_name, "CYAN"),
                dc=self.colored(self.dc, "CYAN"),
            )
        else:
            msg = _("Did not found a datastore cluster in vSphere {vs}, datacenter {dc}.").format(
                vs=self.colored(self.vsphere_name, "CYAN"),
                dc=self.colored(self.dc, "CYAN"),
            )
        LOG.info(msg)

        self.get_datastores()
        len_datastores = len(self.datastores)
        if len_datastores:
            one = pgettext("found_datastore", "one")
            msg = ngettext(
                "Found total {one} datastore in vSphere {vs}, datacenter {dc}.",
                "Found total {nr} datastores in vSphere {vs}, datacenter {dc}.",
                len_datastores,
            )
            msg = msg.format(
                one=self.colored(one, "CYAN"),
                nr=self.colored(str(len_datastores), "CYAN"),
                vs=self.colored(self.vsphere_name, "CYAN"),
                dc=self.colored(self.dc, "CYAN"),
            )
        else:
            msg = _("Did not found a datastore in vSphere {vs}, datacenter {dc}.").format(
                vs=self.colored(self.vsphere_name, "CYAN"),
                dc=self.colored(self.dc, "CYAN"),
            )
        LOG.info(msg)

        if not len_ds_clusters and not len_datastores:
            msg = _(
                "Found neither a datastore cluster nor a datastore in vSphere {vs}, "
                "datacenter {dc}."
            ).format(
                vs=self.colored(self.vsphere_name, "CYAN"),
                dc=self.colored(self.dc, "CYAN"),
            )
            LOG.error(msg)
            self.exit(7)

    # -------------------------------------------------------------------------
    def get_datastore_clusters(self):
        """Retrieve all datastore clusters in current vSphere and datacenter."""
        self.ds_clusters = VsphereDsClusterDict()

        # ----------
        def _get_datastore_clusters():
            try:
                self.cur_vsphere.get_ds_clusters(
                    vsphere_name=self.vsphere_name,
                    search_in_dc=self.dc,
                    warn_if_empty=False,
                    detailled=True,
                )
            except VSphereExpectedError as e:
                LOG.error(str(e))
                self.exit(6)

            for cluster_name in self.cur_vsphere.ds_clusters:
                self.ds_clusters.append(self.cur_vsphere.ds_clusters[cluster_name])

        if self.verbose or self.quiet:
            _get_datastore_clusters()
        else:
            spin_prompt = _("Getting all vSphere storage clusters ...")
            spinner_name = self.get_random_spinner_name()
            with Spinner(spin_prompt, spinner_name):
                _get_datastore_clusters()
            sys.stdout.write(" " * len(spin_prompt))
            sys.stdout.write("\r")
            sys.stdout.flush()

        if self.verbose > 2:
            LOG.debug(_("Found datastore clusters:") + "\n" + pp(self.ds_clusters.as_list()))

    # -------------------------------------------------------------------------
    def get_datastores(self):
        """Retrieve  datastores in current vSphere and datacenter."""
        self.datastores = VsphereDatastoreDict()

        # ----------
        def _get_datastores():
            try:
                self.cur_vsphere.get_datastores(
                    vsphere_name=self.vsphere_name,
                    search_in_dc=self.dc,
                    warn_if_empty=False,
                    detailled=True,
                    no_local_ds=False,
                )
            except VSphereExpectedError as e:
                LOG.error(str(e))
                self.exit(6)

            for ds_name in self.cur_vsphere.datastores:
                self.datastores.append(self.cur_vsphere.datastores[ds_name])

        if self.verbose or self.quiet:
            _get_datastores()
        else:
            spin_prompt = _("Getting all vSphere datastores ...")
            spinner_name = self.get_random_spinner_name()
            with Spinner(spin_prompt, spinner_name):
                _get_datastores()
            sys.stdout.write(" " * len(spin_prompt))
            sys.stdout.write("\r")
            sys.stdout.flush()

        if self.verbose > 0:
            LOG.debug(_("Found datastores:") + "\n" + pp(self.datastores.as_list()))

    # -------------------------------------------------------------------------
    def search_for_space(self):
        """Search in evaluated datastore clusters and datastores for space for a virtual disk."""
        if self.ds_clusters:
            LOG.info(_("Searching for space in evaluated datastore clusters."))
            # LOG.debug(
            #     f"Datastore cluster must be connected with computing cluster {self.cluster!r}")
            try:
                ds_cluster = self.ds_clusters.search_space(
                    needed_gb=self.disk_size_gb,
                    storage_type=self.storage_type,
                    reserve_space=False,
                    compute_cluster=self.cluster,
                )

                msg = "\n " + self.colored("*", "GREEN") + " "
                msg += _("Found usable datastore cluster:") + "\n\n"
                msg += "   " + self.colored(ds_cluster, "CYAN") + "\n"

                print(msg)
                self.exit(0)
            except VSphereNoDsClusterFoundError as e:
                print()
                LOG.warn(str(e))

        if self.datastores:
            LOG.info(_("Searching for space in evaluated datastores."))
            # LOG.debug(f"Datastore must be connected with computing cluster {self.cluster!r}")
            try:
                datastore = self.datastores.search_space(
                    needed_gb=self.disk_size_gb,
                    storage_type=self.storage_type,
                    reserve_space=False,
                    compute_cluster=self.cluster,
                    use_local=True,
                )

                msg = "\n " + self.colored("*", "GREEN") + " "
                msg += _("Found usable datastore:") + "\n\n"
                msg += "   " + self.colored(datastore, "CYAN") + "\n"

                print(msg)
                self.exit(0)
            except VSphereNoDatastoreFoundError as e:
                print()
                LOG.warn(str(e))

        print()
        LOG.warn(_("No datastore cluster or datastore for the given volume."))
        self.exit(3)

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
