#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for the application object of the get-vsphere-vm-info application.

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
from operator import attrgetter

# Third party modules
from fb_tools.spinner import Spinner

# Own modules
from . import BaseVmwareApplication, VmwareAppError
from .. import __version__ as GLOBAL_VERSION
from ..controller import VsphereDiskController
from ..errors import VSphereExpectedError
from ..ether import VsphereEthernetcard
from ..xlate import XLATOR

__version__ = "1.10.0"
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext
ngettext = XLATOR.ngettext


# =============================================================================
class GetVmAppError(VmwareAppError):
    """Base exception class for all exceptions in this application."""

    pass


# =============================================================================
class GetVmApplication(BaseVmwareApplication):
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
        """Initialize the GetVmApplication object."""
        desc = _(
            "Tries to get information about the given virtual machines in "
            "VMware vSphere and print it out."
        )

        self.vms = []

        super(GetVmApplication, self).__init__(
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
        super(GetVmApplication, self).init_arg_parser()

        self.arg_parser.add_argument(
            "vms",
            metavar="VM",
            type=str,
            nargs="+",
            help=_("Names of the VM to get information."),
        )

    # -------------------------------------------------------------------------
    def perform_arg_parser(self):
        """Evaluate the command line parameters. Maybe overridden."""
        super(GetVmApplication, self).perform_arg_parser()

        for vm in self.args.vms:
            self.vms.append(vm)

    # -------------------------------------------------------------------------
    def _run(self):

        LOG.debug(_("Starting {a!r}, version {v!r} ...").format(a=self.appname, v=self.version))

        ret = 99
        try:
            ret = self.show_vms()
        finally:
            self.cleaning_up()

        self.exit(ret)

    # -------------------------------------------------------------------------
    def show_vms(self):
        """Show all virtual machines."""
        ret = 0

        try:
            for vsphere_name in self.vsphere:
                vsphere = self.vsphere[vsphere_name]
                vsphere.get_datacenters()

        except VSphereExpectedError as e:
            LOG.error(str(e))
            self.exit(8)

        for vm_name in sorted(self.vms, key=str.lower):
            if not self.show_vm(vm_name):
                ret = 1

        return ret

    # -------------------------------------------------------------------------
    def show_vm(self, vm_name):
        """Show a particular VM on STDOUT."""
        print()
        msg_tpl = _("Getting data of VM {} ... ")
        if self.verbose:
            msg = msg_tpl.format(self.colored(vm_name, "CYAN"))
            print(msg)
            vm = self._get_vm_data(vm_name)
        else:
            msg_len = len(msg_tpl.format(vm_name))
            spin_prompt = msg_tpl.format(self.colored(vm_name, "CYAN"))
            spinner_name = self.get_random_spinner_name()
            with Spinner(spin_prompt, spinner_name):
                vm = self._get_vm_data(vm_name)
            sys.stdout.write(" " * msg_len)
            sys.stdout.write("\r")
            sys.stdout.flush()

        print("{}: ".format(vm_name), end="")
        if not vm:
            print(self.colored(_("NOT FOUND"), "RED"))
            return False

        # print("{ok}\n{vm}".format(ok=self.colored("OK", 'GREEN'), vm=pp(vm.as_dict(bare=True))))
        print("{ok}".format(ok=self.colored("OK", "GREEN")))
        print()
        print(
            "    State:    {s:<13} Config version: {v}".format(
                s=vm.power_state, v=vm.config_version
            )
        )
        dc_name = "~"
        if vm.dc_name:
            dc_name = vm.dc_name
        msg = "    vSphere:  {vs:<10}    DC: {dc:<25}    Cluster: {cl:<20}    Path: {p}".format(
            vs=vm.vsphere, dc=dc_name, cl=vm.cluster_name, p=vm.path
        )
        print(msg)

        no_cpu = "   -"
        if vm.num_cpu is not None:
            no_cpu = "{:4d}".format(vm.num_cpu)

        ram = "        -"
        if vm.memory_gb is not None:
            ram = "{:5.1f} GiB".format(vm.memory_gb)

        msg = "    No. CPUs: {cp}          RAM: {m}                   Cfg-Path: {p}".format(
            cp=no_cpu, m=ram, p=vm.config_path
        )
        print(msg)

        os_id = "{:<43}".format("-")
        if vm.guest_id is not None:
            os_id = "{:<43}".format(vm.guest_id)

        os_name = _("Unknown")
        if vm.guest_fullname is not None:
            os_name = vm.guest_fullname

        print("    OS:       {id}    {os}".format(id=os_id, os=os_name))

        self._print_ctrlrs(vm)
        self._print_disks(vm)
        self._print_interfaces(vm)
        self._print_custom_data(vm)

        return True

    # -------------------------------------------------------------------------
    def _print_ctrlrs(self, vm):

        ctrl_lbl = _("Controller") + ":"
        len_ctrl_lbl = len(ctrl_lbl)

        len_no_disk = 1
        len_ctrl_no = 1
        for ctrlr in filter(lambda x: x.scsi_ctrl_nr is not None, vm.controllers):
            nr_disks = len(ctrlr.devices)
            no_disk = ngettext("{nr:>2} disk ", "{nr:>2} disks", nr_disks).format(nr=nr_disks)
            if len(no_disk) > len_no_disk:
                len_no_disk = len(no_disk)
            if len(str(ctrlr.bus_nr)) > len_ctrl_no:
                len_ctrl_no = len(str(ctrlr.bus_nr))

        line_template = (
            f"    {{la:<{len_ctrl_lbl}}}  {{nr:>{len_ctrl_no}}} - {{di:<{len_no_disk}}} - {{ty}}"
        )
        # LOG.debug(f"Line template: {line_template!r}")

        first = True
        for ctrlr in sorted(
            filter(lambda x: x.scsi_ctrl_nr is not None, vm.controllers), key=attrgetter("bus_nr")
        ):
            if ctrlr.scsi_ctrl_nr is None:
                continue
            label = ""
            if first:
                label = ctrl_lbl
            first = False
            ctype = _("Unknown")
            nr_disks = len(ctrlr.devices)
            if ctrlr.ctrl_type in VsphereDiskController.type_names.keys():
                ctype = VsphereDiskController.type_names[ctrlr.ctrl_type]
            no_disk = ngettext("{nr:>2} disk ", "{nr:>2} disks", nr_disks).format(nr=nr_disks)
            msg = line_template.format(la=label, nr=ctrlr.bus_nr, di=no_disk, ty=ctype)
            print(msg)

    # -------------------------------------------------------------------------
    def _print_disks(self, vm):

        if not vm.disks:
            print("    " + _("Disks") + ":       " + _("None"))
            return

        ctrl_lbl = _("Controller")
        file_lbl = _("File")
        len_disk_lbl = 1
        len_ctrl_lbl = len(ctrl_lbl)
        len_ctrlr_nr = 1

        for disk in vm.disks:
            if len(disk.label) > len_disk_lbl:
                len_disk_lbl = len(disk.label)
            ctrlr_nr = -1
            for ctrlr in vm.controllers:
                if disk.key in ctrlr.devices:
                    ctrlr_nr = ctrlr.bus_nr
                    break
            if len(str(ctrlr_nr)) > len_ctrlr_nr:
                len_ctrlr_nr = len(str(ctrlr_nr))

        line_template = f"    {{la}}  {{n:<{len_disk_lbl}}}"
        line_template += f" - {{s:7.1f}} GiB - {{ctrl_lbl:<{len_ctrl_lbl}}}"
        line_template += f" {{c:>{len_ctrlr_nr}}}"
        line_template += " - {file_lbl} {f}"
        # LOG.debug(f"Line template: {line_template!r}")

        total_gb = 0.0
        first = True
        for disk in vm.disks:
            total_gb += disk.size_gb
            label = " " * 15
            if first:
                label = (ngettext("Disk", "Disks", len(vm.disks)) + ":").ljust(15)
            first = False
            ctrlr_nr = -1
            for ctrlr in vm.controllers:
                if disk.key in ctrlr.devices:
                    ctrlr_nr = ctrlr.bus_nr
                    break
            msg = line_template.format(
                la=label,
                n=disk.label,
                s=disk.size_gb,
                ctrl_lbl=ctrl_lbl,
                c=ctrlr_nr,
                file_lbl=file_lbl,
                f=disk.file_name,
            )
            print(msg)
        if len(vm.disks) > 1:
            msg = (" " * 21) + "{n:<15} - {s:7.1f} GiB".format(n=_("Total"), s=total_gb)
            print(msg)

    # -------------------------------------------------------------------------
    def _print_interfaces(self, vm):

        if not vm.interfaces:
            print("    Ethernet:    {}".format(_("None")))
            return

        first = True
        for dev in vm.interfaces:
            label = " " * 15
            if first:
                label = "Ethernet:".ljust(15)
            first = False
            etype = _("Unknown")
            if dev.ether_type in VsphereEthernetcard.ether_types.keys():
                etype = VsphereEthernetcard.ether_types[dev.ether_type]
            msg = "    {la}  {n:<15} - Network {nw:<20} - Connection: {c:<4} - {t}".format(
                la=label, n=dev.label, nw=dev.backing_device, c=dev.connect_status, t=etype
            )
            print(msg)

    # -------------------------------------------------------------------------
    def _print_custom_data(self, vm):

        if not vm.custom_data:
            return

        no_vals = len(vm.custom_data)

        label = ngettext("Custom Value", "Custom Values", no_vals)
        print("    {}:".format(label))

        max_key_len = 1
        for custom_data in vm.full_custom_data:
            for custom_name in custom_data.keys():
                if len(custom_name) > max_key_len:
                    max_key_len = len(custom_name)
        max_key_len += 1
        for custom_data in vm.full_custom_data:
            for custom_name in custom_data.keys():
                custom_value = custom_data[custom_name]
                name = custom_name + ":"
                line = "        - {n:<{len}} {val}".format(
                    n=name, len=max_key_len, val=custom_value
                )
                print(line.rstrip())

    # -------------------------------------------------------------------------
    def _get_vm_data(self, vm_name):

        if self.verbose > 1:
            LOG.debug(_("Pulling full data of VM {!r} ...").format(vm_name))

        vm = None

        for vsphere_name in self.vsphere:
            vsphere = self.vsphere[vsphere_name]
            LOG.debug(
                _("Searching for VM {vm} in vSphere {vs} ...").format(
                    vm=self.colored(vm_name, "CYAN"), vs=self.colored(vsphere_name, "CYAN")
                )
            )
            vm = vsphere.get_vm_direct(vm_name, vsphere_name=vsphere_name, no_error=True)
            # vm = vsphere.get_vm(vm_name, vsphere_name=vsphere_name, no_error=True)
            if not vm:
                continue

            vm.full_custom_data = []
            if vm.custom_data:
                for cdata in vm.custom_data:
                    for custom_key in cdata.keys():
                        custom_value = cdata[custom_key]
                        custom_name = vsphere.custom_field_name(custom_key)
                        if custom_name is None:
                            custom_name = custom_key
                        vm.full_custom_data.append({custom_name: custom_value})

            if vm:
                break

        return vm


# =============================================================================
def main():
    """Entrypoint for get-vsphere-vm-info."""
    my_path = pathlib.Path(__file__)
    appname = my_path.name

    locale.setlocale(locale.LC_ALL, "")

    app = GetVmApplication(appname=appname)
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
