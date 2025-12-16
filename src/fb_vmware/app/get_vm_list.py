#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for the application object of the get-vsphere-vm-list application.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import absolute_import, print_function

# Standard modules
import argparse
import locale
import logging
import pathlib
import re
import sys
from operator import attrgetter, itemgetter

# Third party modules
from fb_tools.argparse_actions import RegexOptionAction
from fb_tools.common import is_sequence
from fb_tools.common import pp
from fb_tools.common import to_bool
from fb_tools.spinner import Spinner
from fb_tools.xlate import format_list

# Own modules
from . import BaseVmwareApplication, VmwareAppError
from .. import __version__ as GLOBAL_VERSION
from ..errors import VSphereExpectedError
from ..vm import VsphereVm
from ..xlate import XLATOR

__version__ = "1.11.1"
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext
ngettext = XLATOR.ngettext


# =============================================================================
class GetVmListAppError(VmwareAppError):
    """Base exception class for all exceptions in this application."""

    pass


# =============================================================================
class RegexListOptionAction(argparse.Action):
    """An argparse action for regular expressions."""

    # -------------------------------------------------------------------------
    def __init__(self, option_strings, topic, re_options=None, *args, **kwargs):
        """Initialise a RegexListOptionAction object."""
        self._topic = topic
        self._re_options = None
        if re_options is not None:
            self._re_options = re_options

        super(RegexListOptionAction, self).__init__(*args, option_strings=option_strings, **kwargs)

    # -------------------------------------------------------------------------
    def __call__(self, parser, namespace, pattern, option_string=None):
        """Parse the regular expression option."""
        try:
            if is_sequence(pattern):
                if len(pattern) > 1:
                    used_pattern = []
                    for pat in pattern:
                        used_pattern.append("(" + pat + ")")
                    pattern_all = "|".join(used_pattern)
                elif len(pattern) == 1:
                    pattern_all = pattern[0]
                else:
                    pattern_all = None
            else:
                pattern_all = pattern

            if pattern_all is not None:
                if self._re_options is None:
                    re_test = re.compile(pattern_all)  # noqa
                else:
                    re_test = re.compile(pattern_all, self._re_options)  # noqa
        except Exception as e:
            msg = _("Got a {c} for pattern {p!r}: {e}").format(
                c=e.__class__.__name__, p=pattern_all, e=e
            )
            raise argparse.ArgumentError(self, msg)

        setattr(namespace, self.dest, pattern_all)


# =============================================================================
class GetVmListApplication(BaseVmwareApplication):
    """Class for the application objects."""

    default_vm_pattern = r".*"
    avail_sort_keys = (
        "name",
        "vsphere",
        "dc",
        "cluster",
        "path",
        "type",
        "onl_str",
        "cfg_ver",
        "os",
    )
    default_sort_keys = ["name", "vsphere", "dc"]

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
        """Initialize a GetVmListApplication object."""
        desc = _(
            "Tries to get a list of all virtual machines in " "VMware vSphere and print it out."
        )

        self._vm_pattern = self.default_vm_pattern
        self._details = False

        self.sort_keys = self.default_sort_keys

        self._re_hw = None
        self._re_os = None

        self.vms = []

        super(GetVmListApplication, self).__init__(
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
    def vm_pattern(self):
        """Return the regex search pattern for filtering the VM list."""
        return self._vm_pattern

    # -------------------------------------------------------------------------
    @property
    def details(self):
        """Return whther the list should be displyed with all details."""
        return self._details

    @details.setter
    def details(self, value):
        self._details = to_bool(value)

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transform the elements of the object into a dict.

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """
        res = super(GetVmListApplication, self).as_dict(short=short)
        res["details"] = self.details
        res["vm_pattern"] = self.vm_pattern
        res["default_vm_pattern"] = self.default_vm_pattern

        return res

    # -------------------------------------------------------------------------
    def post_init(self):
        """
        Execute some things before calling run().

        Here could be done some finishing actions after reading in
        commandline parameters, configuration a.s.o.
        """
        super(GetVmListApplication, self).post_init()

        self.initialized = True

    # -------------------------------------------------------------------------
    def init_arg_parser(self):
        """Initiate the argument parser."""
        super(GetVmListApplication, self).init_arg_parser()

        filter_group = self.arg_parser.add_argument_group(_("Filter options"))

        filter_group.add_argument(
            dest="vm_pattern",
            nargs="*",
            metavar="REGEX",
            action=RegexListOptionAction,
            topic=_("for names of VMs"),
            re_options=re.IGNORECASE,
            help=_(
                "A regular expression to filter the output list of VMs by their name "
                "(Default: {!r})."
            ).format(self.default_vm_pattern),
        )

        valid_vm_types = ("all", "vm", "template")
        filter_group.add_argument(
            "-T",
            "--type",
            metavar=_("TYPE"),
            dest="vm_type",
            choices=valid_vm_types,
            default="all",
            help=_(
                "Filter output for the type of the VM. Valid values are {li} "
                "(Default: {dflt!r})."
            ).format(dflt="all", li=format_list(valid_vm_types, do_repr=True)),
        )

        online_filter = filter_group.add_mutually_exclusive_group()
        online_filter.add_argument(
            "--on",
            "--online",
            action="store_true",
            dest="online",
            help=_("Filter output for online VMs."),
        )
        online_filter.add_argument(
            "--off",
            "--offline",
            action="store_true",
            dest="offline",
            help=_("Filter output for offline VMs and templates."),
        )

        filter_group.add_argument(
            "-H",
            "--hw",
            "--hardware-config",
            metavar="REGEX",
            action=RegexOptionAction,
            dest="hw",
            topic=_("for VMware hardware config version"),
            re_options=re.IGNORECASE,
            help=_(
                "A regular expression to filter the output list of VMs by the VMware hardware "
                "configuration version (e.g. '{}')."
            ).format(r"vmx-0\d$"),
        )

        filter_group.add_argument(
            "--os",
            metavar="REGEX",
            action=RegexOptionAction,
            dest="os",
            topic=_("for the Operating System version"),
            re_options=re.IGNORECASE,
            help=_(
                "A regular expression to filter the output list of VMs by their Operating "
                "System version, e.g. '{}'."
            ).format("oracleLinux.*(_64)?Guest"),
        )

        output_options = self.arg_parser.add_argument_group(_("Output options"))

        output_options.add_argument(
            "-D",
            "--details",
            dest="details",
            action="store_true",
            help=_("Detailed output list (quering data needs some time longer)."),
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
        """Evaluate the command line parameters."""
        super(GetVmListApplication, self).perform_arg_parser()

        if self.args.details:
            self.details = self.args.details

        if self.args.vm_pattern:
            try:
                re_name = re.compile(self.args.vm_pattern, re.IGNORECASE)
                LOG.debug(_("Regular expression for filtering: {!r}").format(re_name.pattern))
                self._vm_pattern = self.args.vm_pattern
            except Exception as e:
                msg = _("Got a {c} for pattern {p!r}: {e}").format(
                    c=e.__class__.__name__, p=self.args.vm_pattern, e=e
                )
                LOG.error(msg)

        if not self.details:
            if (
                self.args.online
                or self.args.offline
                or self.args.hw
                or self.args.os
                or self.args.vm_type != "all"
            ):
                LOG.info(_("Detailed output is required because of your given options."))
                self.details = True

        if self.args.sort_keys:
            if self.details:
                self.sort_keys = self.args.sort_keys
            else:
                self.sort_keys = []
                for key in self.args.sort_keys:
                    if key in ("name", "vsphere", "path"):
                        self.sort_keys.append(key)
                    else:
                        LOG.warn(
                            _(
                                "Sorting key {!r} not usable, if not detailed output " "was given."
                            ).format(key)
                        )
                if not self.sort_keys:
                    LOG.warn(
                        _("No usable sorting keys found, using default sorting keys {}.").format(
                            format_list(self.default_sort_keys, do_repr=True)
                        )
                    )
                    self.sort_keys = self.default_sort_keys

        if self.args.hw:
            self._re_hw = re.compile(self.args.hw, re.IGNORECASE)
        if self.args.os:
            self._re_os = re.compile(self.args.os, re.IGNORECASE)

    # -------------------------------------------------------------------------
    def _run(self):

        LOG.debug(_("Starting {a!r}, version {v!r} ...").format(a=self.appname, v=self.version))

        ret = 0
        try:
            ret = self.get_all_vms()
        except VSphereExpectedError as e:
            LOG.error(str(e))
            self.exit(6)
        finally:
            self.cleaning_up()

        self.exit(ret)

    # -------------------------------------------------------------------------
    def get_all_vms(self):
        """Get all VMs from vSphere, maybe filtered."""
        ret = 0
        all_vms = []

        re_name = re.compile(self.vm_pattern, re.IGNORECASE)

        if self.verbose:
            for vsphere_name in self.vsphere:
                all_vms += self.get_vms(vsphere_name, re_name)
        elif not self.quiet:
            spin_prompt = _("Getting all vSphere VMs ...") + " "
            spinner_name = self.get_random_spinner_name()
            with Spinner(spin_prompt, spinner_name):
                for vsphere_name in self.vsphere:
                    all_vms += self.get_vms(vsphere_name, re_name)
            sys.stdout.write(" " * len(spin_prompt))
            sys.stdout.write("\r")
            sys.stdout.flush()

        if self.verbose > 1:
            LOG.debug(_("Using sorting keys:") + " " + format_list(self.sort_keys, do_repr=True))

        if self.details:
            self.print_vms_detailed(all_vms)
        else:
            self.print_vms(all_vms)

        return ret

    # -------------------------------------------------------------------------
    def print_vms(self, all_vms):
        """Print out on STDOUT the list of found VMs."""
        label_list = ("name", "vsphere", "dc", "path")
        labels = {
            "name": _("Host"),
            "vsphere": "vSphere",
            "dc": _("Data Center"),
            "path": _("Path"),
        }

        self._print_vms(all_vms, label_list, labels)

    # -------------------------------------------------------------------------
    def print_vms_detailed(self, all_vms):
        """Print out on STDOUT the list of found VMs in a detailled way."""
        label_list = self.avail_sort_keys
        labels = {
            "name": "VM/Template",
            "vsphere": "vSphere",
            "dc": _("Data Center"),
            "cluster": _("Cluster"),
            "path": _("Path"),
            "type": _("Type"),
            "onl_str": _("Online Status"),
            "cfg_ver": _("Config Version"),
            "os": _("Operating System"),
        }

        self._print_vms(all_vms, label_list, labels)

    # -------------------------------------------------------------------------
    def _print_vms(self, all_vms, label_list, labels):

        str_lengths = {}
        for label in labels.keys():
            str_lengths[label] = len(labels[label])

        max_len = 0
        count = 0
        for cdata in all_vms:
            for field in ("cluster", "path", "type", "cfg_ver", "os"):
                if field in labels and cdata[field] is None:
                    cdata[field] = "~"
            for label in labels.keys():
                val = cdata[label]
                if len(val) > str_lengths[label]:
                    str_lengths[label] = len(val)

        for label in labels.keys():
            if max_len:
                max_len += 2
            max_len += str_lengths[label]

        if self.verbose > 1:
            LOG.debug("Label length:\n" + pp(str_lengths))
            LOG.debug("Max line length: {} chars".format(max_len))

        tpl = ""
        for label in label_list:
            if tpl != "":
                tpl += "  "
            tpl += "{{{la}:<{le}}}".format(la=label, le=str_lengths[label])
        if self.verbose > 1:
            LOG.debug(_("Line template: {}").format(tpl))

        if not self.quiet:
            print()
            print(tpl.format(**labels))
            print("-" * max_len)

        all_vms.sort(key=itemgetter(*self.sort_keys))

        for cdata in all_vms:
            count += 1

            print(tpl.format(**cdata))

        if not self.quiet:
            print()
            if count == 0:
                msg = _("Found no VMware VMs.")
            else:
                msg = ngettext("Found one VMware VM.", "Found {} VMware VMs.", count).format(count)
            print(msg)
            print()

    # -------------------------------------------------------------------------
    def get_vms(self, vsphere_name, re_name=None):
        """Get the filtered list of VMs from vSphere."""
        vsphere = self.vsphere[vsphere_name]
        vsphere.get_datacenter()

        if re_name is None:
            re_name = re.compile(self.vm_pattern, re.IGNORECASE)

        if self.details:
            # vm_list = vsphere.get_vms(re_name, vsphere_name=vsphere_name, as_obj=True)
            vm_list = vsphere.get_vm_list(
                re_name, vsphere_name=vsphere_name, name_only=False, disconnect=True
            )
            vms = self.mangle_vmlist_details(vm_list, vsphere_name)
        else:
            # vm_list = vsphere.get_vms(re_name, vsphere_name=vsphere_name, name_only=True)
            vm_list = vsphere.get_vm_list(
                re_name, vsphere_name=vsphere_name, name_only=True, disconnect=True
            )
            vms = self.mangle_vmlist_no_details(vm_list, vsphere_name)

        return vms

    # -------------------------------------------------------------------------
    def mangle_vmlist_no_details(self, vm_list, vsphere_name):
        """Prepare the non-detailled data about found VMs for output."""
        if self.verbose > 3:
            LOG.debug("Mangling VM list:\n" + pp(vm_list))

        vms = []
        first = True

        for vm in sorted(vm_list, key=itemgetter(0, 1)):

            if self.verbose > 2 and first:
                LOG.debug("VM:\n" + pp(vm))

            cdata = {
                "vsphere": vsphere_name,
                "name": vm[0],
                "dc": vm[1],
                "path": vm[2],
            }

            if cdata["path"]:
                cdata["path"] = cdata["path"]
            else:
                cdata["path"] = "/"

            if self.verbose > 2 and first:
                LOG.debug("Mangled VM:\n" + pp(cdata))

            first = False

            vms.append(cdata)

        return vms

    # -------------------------------------------------------------------------
    def mangle_vmlist_details(self, vm_list, vsphere_name):
        """Prepare the detailled data about found VMs for output."""
        vms = []

        first = True
        for vm in sorted(vm_list, key=attrgetter("name", "path")):

            if not isinstance(vm, VsphereVm):
                msg = _("Found a {} object:").format(vm.__class__.__name__)
                msg += "\n" + pp(vm)
                LOG.error(msg)
                continue

            if self.verbose > 2 and first:
                LOG.debug("VM:\n" + pp(vm.as_dict()))

            cdata = self._mangle_vm_details(vm, vsphere_name)
            if self.verbose > 2 and first and cdata:
                LOG.debug("Mangled VM:\n" + pp(cdata))

            first = False

            if not cdata:
                continue

            vms.append(cdata)

        return vms

    # -------------------------------------------------------------------------
    def _mangle_vm_details(self, vm, vsphere_name):

        cdata = None

        if self.args.vm_type != "all":
            if self.args.vm_type == "vm":
                if vm.template:
                    return None
            else:
                if not vm.template:
                    return None

        if self.args.online:
            if not vm.online:
                return None
        elif self.args.offline:
            if vm.online:
                return None

        if self._re_hw:
            if not self._re_hw.search(vm.config_version):
                return None

        if self._re_os:
            if not self._re_os.search(vm.config_version):
                return None

        dc = "~"
        if vm.dc_name:
            dc = vm.dc_name

        cdata = {
            "vsphere": vsphere_name,
            "dc": dc,
            "cluster": vm.cluster_name,
            "name": vm.name,
            "path": vm.path,
            "type": "Virtual Machine",
            "online": vm.online,
            "onl_str": "Online",
            "cfg_ver": vm.config_version,
            "os": vm.guest_id,
        }

        if cdata["path"]:
            cdata["path"] = cdata["path"]
        else:
            cdata["path"] = "/"

        if not cdata["cluster"]:
            cdata["cluster"] = None

        if not cdata["os"]:
            cdata["os"] = None

        if not vm.online:
            cdata["onl_str"] = "Offline"

        if vm.template:
            cdata["type"] = "VMware Template"

        return cdata


# =============================================================================
def main():
    """Entrypoint for get-vsphere-vm-list."""
    my_path = pathlib.Path(__file__)
    appname = my_path.name

    locale.setlocale(locale.LC_ALL, "")

    app = GetVmListApplication(appname=appname)
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
