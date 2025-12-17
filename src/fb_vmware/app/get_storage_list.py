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

# Own modules
from . import BaseVmwareApplication
from . import VmwareAppError
from .. import __version__ as GLOBAL_VERSION
from ..datastore import VsphereDatastoreDict
from ..errors import VSphereExpectedError
from ..xlate import XLATOR

__version__ = "1.1.0"
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
    def as_dict(self, short=True):
        """
        Transform the elements of the object into a dict.

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """
        res = super(GetStorageListApp, self).as_dict(short=short)
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
            vsphere.get_datastores(no_local_ds=no_local_ds)
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

                datastore["hosts"] = str(len(ds.hosts))

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
                    datastore["usage_pc_out"] = "- %"

                datastore_list.append(datastore)

        if self.print_total:
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
    def _get_ds_fields_len(self, datastore_list, labels):

        field_length = {}

        for label in labels.keys():
            field_length[label] = len(labels[label])

        for ds in datastore_list:
            for label in labels.keys():
                field = ds[label]
                if len(field) > field_length[label]:
                    field_length[label] = len(field)

        if self.totals:
            for label in labels.keys():
                field = self.totals[label]
                if len(field) > field_length[label]:
                    field_length[label] = len(field)

        return field_length

    # -------------------------------------------------------------------------
    def print_datastores(self, all_datastores):
        """Print on STDOUT all information about all datastore clusters."""
        labels = {
            "ds_name": _("Datastore"),
            "hosts": "Hosts",
            "vsphere_name": "vSphere",
            "dc": _("Data Center"),
            "cluster": _("Cluster"),
            "capacity_gb": _("Capacity in GB"),
            "free_space_gb": _("Free space in GB"),
            "usage_gb": _("Calculated usage in GB"),
            "usage_pc_out": _("Usage in percent"),
        }

        label_list = (
            "ds_name",
            "vsphere_name",
            "dc",
            "cluster",
            "hosts",
            "capacity_gb",
            "usage_gb",
            "usage_pc_out",
            "free_space_gb",
        )

        datastore_list = self._get_datastore_list(all_datastores)
        field_length = self._get_ds_fields_len(datastore_list, labels)

        max_len = 0
        count = len(datastore_list)

        for label in labels.keys():
            if max_len:
                max_len += 2
            max_len += field_length[label]

        if self.verbose > 2:
            LOG.debug("Label length:\n" + pp(field_length))
            LOG.debug("Max line length: {} chars".format(max_len))
            LOG.debug("Datastore clusters:\n" + pp(datastore_list))

        tpl = ""
        for label in label_list:
            if tpl != "":
                tpl += "  "
            if label in ("ds_name", "vsphere_name", "dc", "cluster"):
                tpl += "{{{la}:<{le}}}".format(la=label, le=field_length[label])
            else:
                tpl += "{{{la}:>{le}}}".format(la=label, le=field_length[label])
        if self.verbose > 1:
            LOG.debug(_("Line template: {}").format(tpl))

        if self.sort_keys:
            LOG.debug("Sorting keys: " + pp(self.sort_keys))
            self.sort_keys.reverse()
            for key in self.sort_keys:
                if key in ("ds_name", "vsphere_name", "dc", "cluster"):
                    datastore_list.sort(key=itemgetter(key))
                else:
                    datastore_list.sort(key=itemgetter(key), reverse=True)

        if not self.quiet:
            print()
            print(tpl.format(**labels))
            print("-" * max_len)

        for datastore in datastore_list:
            print(tpl.format(**datastore))

        if self.totals:
            if not self.quiet:
                print("-" * max_len)
            print(tpl.format(**self.totals))

        if not self.quiet:
            print()
            if count:
                msg = ngettext(
                    "Found one VMware datastore.",
                    "Found {} VMware datastores.",
                    count,
                ).format(count)
            else:
                msg = _("No VMware datastores found.")

            print(msg)
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

    app()

    return 0


# =============================================================================
if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
