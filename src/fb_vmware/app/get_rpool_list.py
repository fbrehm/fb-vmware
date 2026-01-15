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
from ..cluster import VsphereCluster
from ..errors import VSphereExpectedError

__version__ = "0.1.0"
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
    default_sort_keys = ["vsphere", "dc_name", "name"}

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

        super(GetHostsListApplication, self).__init__(
            appname=appname,
            verbose=verbose,
            version=version,
            base_dir=base_dir,
            description=desc,
            initialized=False,
        )

        self.initialized = True





