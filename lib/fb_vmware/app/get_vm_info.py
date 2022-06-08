#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 by Frank Brehm, Berlin
@summary: The module for the application object of the get-vsphere-vm-info application.
"""
from __future__ import absolute_import, print_function

# Standard modules
import logging

from operator import attrgetter

# Third party modules

# Own modules
from .. import __version__ as GLOBAL_VERSION

from ..errors import VSphereExpectedError

from ..xlate import XLATOR

from . import BaseVmwareApplication, VmwareAppError

from ..controller import VsphereDiskController

from ..ether import VsphereEthernetcard

__version__ = '1.6.0'
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext
ngettext = XLATOR.ngettext


# =============================================================================
class GetVmAppError(VmwareAppError):
    """ Base exception class for all exceptions in this application."""
    pass


# =============================================================================
class GetVmApplication(BaseVmwareApplication):
    """
    Class for the application objects.
    """

    # -------------------------------------------------------------------------
    def __init__(
        self, appname=None, verbose=0, version=GLOBAL_VERSION, base_dir=None,
            initialized=False, usage=None, description=None,
            argparse_epilog=None, argparse_prefix_chars='-', env_prefix=None):

        desc = _(
            "Tries to get information about the given virtual machines in "
            "VMWare VSphere and print it out.")

        self.vms = []

        super(GetVmApplication, self).__init__(
            appname=appname, verbose=verbose, version=version, base_dir=base_dir,
            description=desc, initialized=False,
        )

        self.initialized = True

    # -------------------------------------------------------------------------
    def init_arg_parser(self):
        """
        Public available method to initiate the argument parser.
        """

        super(GetVmApplication, self).init_arg_parser()

        self.arg_parser.add_argument(
            'vms', metavar='VM', type=str, nargs='+',
            help=_('Names of the VM to get information.'),
        )

    # -------------------------------------------------------------------------
    def perform_arg_parser(self):

        super(GetVmApplication, self).perform_arg_parser()

        for vm in self.args.vms:
            self.vms.append(vm)

    # -------------------------------------------------------------------------
    def _run(self):

        LOG.debug(_("Starting {a!r}, version {v!r} ...").format(
            a=self.appname, v=self.version))

        ret = 99
        try:
            ret = self.show_vms()
        finally:
            self.cleaning_up()

        self.exit(ret)

    # -------------------------------------------------------------------------
    def show_vms(self):

        ret = 0

        try:
            for vsphere_name in self.vsphere:
                vsphere = self.vsphere[vsphere_name]
                vsphere.get_datacenter()

        except VSphereExpectedError as e:
            LOG.error(str(e))
            self.exit(8)

        for vm_name in sorted(self.vms, key=str.lower):
            if not self.show_vm(vm_name):
                ret = 1

        return ret

    # -------------------------------------------------------------------------
    def show_vm(self, vm_name):

        print('\n{}: '.format(vm_name), end='')
        if self.verbose:
            print()
        vm = None
        for vsphere_name in self.vsphere:
            vsphere = self.vsphere[vsphere_name]
            vm = vsphere.get_vm(vm_name, vsphere_name=vsphere_name, no_error=True, as_obj=True)
            if vm:
                break

        if not vm:
            print(self.colored(_("NOT FOUND"), 'RED'))
            return False

        # print("{ok}\n{vm}".format(ok=self.colored("OK", 'GREEN'), vm=pp(vm.as_dict(bare=True))))
        print("{ok}".format(ok=self.colored("OK", 'GREEN')))
        print()
        print("    State:    {s:<13} Config version: {v}".format(
            s=vm.power_state, v=vm.config_version))
        msg = "    VSPhere:  {vs:<10}    Cluster: {cl:<20}    Path: {p}".format(
            vs=vm.vsphere, cl=vm.cluster_name, p=vm.path)
        print(msg)

        no_cpu = '   -'
        if vm.num_cpu is not None:
            no_cpu = '{:4d}'.format(vm.num_cpu)

        ram = '        -'
        if vm.memory_gb is not None:
            ram = '{:5.1f} GiB'.format(vm.memory_gb)

        msg = "    No. CPUs: {cp}          RAM: {m}                   Cfg-Path: {p}".format(
            cp=no_cpu, m=ram, p=vm.config_path)
        print(msg)

        os_id = '{:<43}'.format('-')
        if vm.guest_id is not None:
            os_id = '{:<43}'.format(vm.guest_id)

        os_name = _('Unknown')
        if vm.guest_fullname is not None:
            os_name = vm.guest_fullname

        print("    OS:       {id}    {os}".format(id=os_id, os=os_name))

        first = True
        for ctrlr in sorted(
                filter(lambda x: x.scsi_ctrl_nr is not None, vm.controllers),
                key=attrgetter('bus_nr')):
            if ctrlr.scsi_ctrl_nr is None:
                continue
            label = ''
            if first:
                label = 'Controller:'
            first = False
            ctype = _('Unknown')
            nr_disks = len(ctrlr.devices)
            if ctrlr.ctrl_type in VsphereDiskController.type_names.keys():
                ctype = VsphereDiskController.type_names[ctrlr.ctrl_type]
            no_disk = ngettext("{nr:>2} disk ", "{nr:>2} disks", nr_disks).format(
                nr=nr_disks)
            # no_disk = _("{nr:>2} disks").format(nr=len(ctrlr.devices))
            # if len(ctrlr.devices) == 1:
            #     no_disk = _(" 1 disk ")
            msg = "    {la:<15}  {nr:>2} - {di} - {ty}".format(
                la=label, nr=ctrlr.bus_nr, di=no_disk, ty=ctype)
            print(msg)

        if vm.disks:
            total_gb = 0.0
            first = True
            for disk in vm.disks:
                total_gb += disk.size_gb
                label = ' ' * 15
                if first:
                    label = (ngettext('Disk', 'Disks', len(vm.disks)) + ':').ljust(15)
                first = False
                ctrlr_nr = -1
                for ctrlr in vm.controllers:
                    if disk.key in ctrlr.devices:
                        ctrlr_nr = ctrlr.bus_nr
                        break
                msg = "    {la}  {n:<15} - {s:7.1f} GiB - Controller {c:>2} - File {f}".format(
                    la=label, n=disk.label, s=disk.size_gb, c=ctrlr_nr, f=disk.file_name)
                print(msg)
            if len(vm.disks) > 1:
                msg = (' ' * 21) + '{n:<15} - {s:7.1f} GiB'.format(n=_('Total'), s=total_gb)
                print(msg)
        else:
            print("    Disks:       {}".format(_('None')))

        if vm.interfaces:
            first = True
            for dev in vm.interfaces:
                label = ' ' * 15
                if first:
                    label = 'Ethernet:'.ljust(15)
                first = False
                etype = _('Unknown')
                if dev.ether_type in VsphereEthernetcard.ether_types.keys():
                    etype = VsphereEthernetcard.ether_types[dev.ether_type]
                msg = "    {la}  {n:<15} - Network {nw:<20} - Connection: {c:<4} - {t}".format(
                    la=label, n=dev.label, nw=dev.backing_device, c=dev.connect_status, t=etype)
                print(msg)
        else:
            print("    Ethernet:    {}".format(_('None')))

        return True


# =============================================================================
if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
