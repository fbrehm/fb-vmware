#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: A base module for all VMware/vSphere application classes.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 by Frank Brehm, Berlin
"""
from __future__ import absolute_import, print_function

# Standard modules
import copy
import logging
import os
import pathlib
import random

# Third party modules
import fb_tools.spinner
from fb_tools.cfg_app import FbConfigApplication
from fb_tools.common import pp
from fb_tools.errors import FbAppError
from fb_tools.multi_config import DEFAULT_ENCODING

import pytz

from rich.console import Console
from rich.prompt import InvalidResponse, Prompt, PromptBase, PromptType

# Own modules
from .. import __version__ as GLOBAL_VERSION
from ..config import VmwareConfiguration
from ..connect import VsphereConnection
from ..errors import VSphereExpectedError
from ..xlate import DOMAIN
from ..xlate import LOCALE_DIR
from ..xlate import XLATOR
from ..xlate import __base_dir__ as __xlate_base_dir__
from ..xlate import __lib_dir__ as __xlate_lib_dir__
from ..xlate import __mo_file__ as __xlate_mo_file__
from ..xlate import __module_dir__ as __xlate_module_dir__

__version__ = "1.6.0"
LOG = logging.getLogger(__name__)
TZ = pytz.timezone("Europe/Berlin")

_ = XLATOR.gettext
ngettext = XLATOR.ngettext


# =============================================================================
class VmwareAppError(FbAppError):
    """Base exception class for all exceptions in all VMware/vSphere application classes."""

    pass


# =============================================================================
class PositiveIntPrompt(PromptBase[int]):
    """A prompt that returns an positive integer greater than zero.

    Example:
        >>> burrito_count = PositiveIntPrompt.ask("How many burritos do you want to order")

    """

    response_type = int
    validate_error_message = "[prompt.invalid]" + _(
        "Please enter a valid positive integer number greater than zero."
    )

    # -------------------------------------------------------------------------
    def process_response(self, value: str) -> PromptType:
        """Process response from user, convert to prompt type.

        Args:
            value (str): String typed by user.

        Raises:
            InvalidResponse: If ``value`` is invalid.

        Returns:
            PromptType: The value to be returned from ask method.
        """
        value = value.strip()
        try:
            return_value: PromptType = self.response_type(value)
            if return_value <= 0:
                raise InvalidResponse(self.validate_error_message)
        except ValueError:
            raise InvalidResponse(self.validate_error_message)

        return return_value


# =============================================================================
class BaseVmwareApplication(FbConfigApplication):
    """Base class for all VMware/vSphere application classes."""

    term_colors = {
        "kitty": "256",
        "256color": "256",
        "16color": "standard",
    }

    default_all_vspheres = True

    # -------------------------------------------------------------------------
    def __init__(
        self,
        appname=None,
        verbose=0,
        version=GLOBAL_VERSION,
        base_dir=None,
        cfg_class=VmwareConfiguration,
        initialized=False,
        usage=None,
        description=None,
        argparse_epilog=None,
        argparse_prefix_chars="-",
        env_prefix=None,
        append_appname_to_stems=True,
        config_dir=None,
        additional_stems=None,
        additional_cfgdirs=None,
        cfg_encoding=DEFAULT_ENCODING,
        use_chardet=True,
    ):
        """Initialize a BaseVmwareApplication object."""
        self.req_vspheres = None
        self.do_vspheres = []
        self.rich_console = None

        if base_dir is None:
            base_dir = pathlib.Path(os.getcwd()).resolve()

        # Hash with all vSphere handler objects
        self.vsphere = {}

        super(BaseVmwareApplication, self).__init__(
            appname=appname,
            verbose=verbose,
            version=version,
            base_dir=base_dir,
            description=description,
            cfg_class=cfg_class,
            append_appname_to_stems=append_appname_to_stems,
            config_dir=config_dir,
            additional_stems=additional_stems,
            additional_cfgdirs=additional_cfgdirs,
            cfg_encoding=cfg_encoding,
            use_chardet=use_chardet,
            initialized=False,
        )

    # -------------------------------------------------------------------------
    def __del__(self):
        """Clean up in emergency case."""
        if self.vsphere.keys():
            self.cleaning_up()

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transform the elements of the object into a dict.

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """
        res = super(BaseVmwareApplication, self).as_dict(short=short)

        res["xlate"]["fb_vmware"] = {
            "__module_dir__": __xlate_module_dir__,
            "__lib_dir__": __xlate_lib_dir__,
            "__base_dir__": __xlate_base_dir__,
            "LOCALE_DIR": LOCALE_DIR,
            "DOMAIN": DOMAIN,
            "__mo_file__": __xlate_mo_file__,
        }

        return res

    # -------------------------------------------------------------------------
    def post_init(self):
        """
        Execute some things before calling run().

        Here could be done some finishing actions after reading in commandline
        parameters, configuration a.s.o.

        This method could be overwritten by descendant classes, these
        methhods should allways include a call to post_init() of the
        parent class.
        """
        self.initialized = False

        super(BaseVmwareApplication, self).post_init()

        if self.verbose > 2:
            LOG.debug(_("{what} of {app} ...").format(what="post_init()", app=self.appname))

        args_color = getattr(self.args, "color", "auto")
        if args_color == "auto":
            self.rich_console = Console()
        else:
            color_system = None
            if args_color == "yes":
                color_term = os.environ.get("COLORTERM", "").strip().lower()
                if color_term in ("truecolor", "24bit"):
                    color_system = "truecolor"
                else:
                    color_system = "standard"
                    term = os.environ.get("TERM", "").strip().lower()
                    _term_name, _hyphen, colors = term.rpartition("-")
                    color_system = self.term_colors.get(colors, "standard")

            self.rich_console = Console(color_system=color_system)

        if not self.cfg.vsphere.keys():
            msg = _("Did not found any configured vSphere environments.")
            LOG.error(msg)
            self.exit(3)

        if self.args.req_vsphere:
            self.req_vspheres = []
            all_found = True
            for vs_name in self.args.req_vsphere:
                LOG.debug(_("Checking for configured vSphere instance {!r} ...").format(vs_name))
                vs = vs_name.strip().lower()
                if vs not in self.cfg.vsphere.keys():
                    all_found = False
                    msg = _(
                        "vSphere {!r} not found in list of configured vSphere instances."
                    ).format(vs_name)
                    LOG.error(msg)
                else:
                    if vs not in self.req_vspheres:
                        self.req_vspheres.append(vs)
            if not all_found:
                self.exit(1)

        if self.req_vspheres:
            self.do_vspheres = copy.copy(self.req_vspheres)
        elif self.default_all_vspheres:
            for vs_name in self.cfg.vsphere.keys():
                self.do_vspheres.append(vs_name)

    # -------------------------------------------------------------------------
    def init_arg_parser(self):
        """Initiate the argument parser."""
        self.add_vsphere_argument()
        super(BaseVmwareApplication, self).init_arg_parser()

    # -------------------------------------------------------------------------
    def add_vsphere_argument(self):
        """Add a commandline option for selecting the vSphere to use."""
        vsphere_options = self.arg_parser.add_argument_group(_("vSphere options"))

        vsphere_options.add_argument(
            "--vs",
            "--vsphere",
            dest="req_vsphere",
            nargs="*",
            help=_("The vSphere names from configuration, in which the VMs should be searched."),
        )

    # -------------------------------------------------------------------------
    def perform_arg_parser(self):
        """Evaluate the command line parameters. Maybe overridden."""
        if self.verbose > 2:
            LOG.debug(_("Got command line arguments:") + "\n" + pp(self.args))

    # -------------------------------------------------------------------------
    def pre_run(self):
        """Execute some actions before the main routine."""
        LOG.debug(_("Actions before running main routine."))

        self.init_vsphere_handlers()

    # -------------------------------------------------------------------------
    def select_vsphere(self):
        """Select exact one of the configured vSpheres."""
        if self.do_vspheres and len(self.do_vspheres) == 1:
            return self.do_vspheres[0]

        if self.do_vspheres:
            msg = _("There are multiple vSpheres selected on commandline.")
            raise VmwareAppError(msg)

        if not self.cfg.vsphere.keys():
            msg = _("There are no configured vSpheres available.")
            raise VmwareAppError(msg)

        vspheres = []
        for vs_name in self.cfg.vsphere.keys():
            vspheres.append(vs_name)

        vsphere = Prompt.ask(
            _("Select the vSphere to search for the a storage location"),
            choices=vspheres,
            show_choices=True,
            console=self.rich_console,
        )

        return vsphere

    # -------------------------------------------------------------------------
    def select_datacenter(self, vs_name, dc_name=None):
        """Select a virtual datacenter from given vSphere."""
        if not vs_name:
            raise VmwareAppError(_("No vSphere name given."))
        if vs_name not in self.vsphere:
            raise VmwareAppError(
                _("vSphere {} is not an active vSphere.").format(self.colored(vs_name, "RED"))
            )

        vsphere = self.vsphere[vs_name]
        vsphere.get_datacenters()
        dc_list = []
        for _dc_name in vsphere.datacenters.keys():
            dc_list.append(_dc_name)

        if not len(dc_list):
            msg = _("Did not found virtual datacenters in vSphere {}.").format(
                self.colored(vs_name, "RED")
            )
            LOG.error(msg)
            return None

        if self.verbose > 2:
            LOG.debug(f"Found datacenters in vSphere {vs_name}:\n" + pp(dc_list))

        if dc_name:
            if dc_name in dc_list:
                return dc_name
            msg = _("Datacenter {dc} does not exists in vSphere {vs}.").format(
                dc=self.colored(dc_name, "RED"), vs=self.colored(vs_name, "CYAN")
            )
            LOG.error(msg)
            return None

        if len(dc_list) == 1:
            if self.verbose > 0:
                LOG.debug(
                    f"Automatic select of datacenter {dc_list[0]!r}, because it is the only one."
                )
            return dc_list[0]

        dc_name = Prompt.ask(
            _("Select a virtual datacenter to search for the a storage location"),
            choices=dc_list,
            show_choices=True,
            console=self.rich_console,
        )

        return dc_name

    # -------------------------------------------------------------------------
    def prompt_for_disk_size(self):
        """Ask for the size of a virtual disk in GiByte."""
        disk_size_gb = PositiveIntPrompt.ask(_("Get the size of the virtual disk in GiByte"))
        return disk_size_gb

    # -------------------------------------------------------------------------
    def init_vsphere_handlers(self):
        """Initialize all vSphere handlers."""
        if self.verbose > 1:
            LOG.debug(_("Initializing vSphere handlers ..."))

        try:
            for vsphere_name in self.do_vspheres:
                self.init_vsphere_handler(vsphere_name)
        except VSphereExpectedError as e:
            LOG.error(str(e))
            self.exit(7)

    # -------------------------------------------------------------------------
    def init_vsphere_handler(self, vsphere_name):
        """Initialize the given vSphere handler."""
        if self.verbose > 2:
            LOG.debug(_("Initializing handler for vSphere {!r} ...").format(vsphere_name))

        vsphere_data = self.cfg.vsphere[vsphere_name]

        vsphere = VsphereConnection(
            vsphere_data,
            auto_close=True,
            simulate=self.simulate,
            force=self.force,
            appname=self.appname,
            verbose=self.verbose,
            base_dir=self.base_dir,
            terminal_has_colors=self.terminal_has_colors,
            initialized=False,
        )

        if vsphere:
            self.vsphere[vsphere_name] = vsphere
            vsphere.initialized = True
        else:
            msg = _("Could not initialize {} object from:").format("VsphereConnection")
            msg += "\n" + str(vsphere_data)
            LOG.error(msg)

        vsphere._check_credentials()

    # -------------------------------------------------------------------------
    def cleaning_up(self):
        """Close all vSphere connections and remove all vSphere handlers."""
        if self.verbose > 1:
            LOG.debug(_("Cleaning up ..."))

        for vsphere_name in self.do_vspheres:
            if vsphere_name in self.vsphere:
                LOG.debug(_("Closing vSphere object {!r} ...").format(vsphere_name))
                self.vsphere[vsphere_name].disconnect()
                del self.vsphere[vsphere_name]

    # -------------------------------------------------------------------------
    @classmethod
    def get_random_spinner_name(cls):
        """Return a randon spinner name from fb_tools.spinner.CycleList."""
        randomizer = random.SystemRandom()

        return randomizer.choice(list(fb_tools.spinner.CycleList.keys()))


# =============================================================================
if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
