#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 by Frank Brehm, Berlin
@summary: The module for a base VSphere handler object.
"""
from __future__ import absolute_import

# Standard modules
import logging

# Third party modules

# Own modules
from .xlate import XLATOR

from base import BaseVsphereHandler

__version__ = '0.2.0'

LOG = logging.getLogger(__name__)

_ = XLATOR.gettext

DEFAULT_HOST = 'vcs01.ppbrln.internal'
DEFAULT_PORT = 443
DEFAULT_USER = 'Administrator@vsphere.local'
DEFAULT_DC = 'vmcc'
DEFAULT_CLUSTER = 'vmcc-l105-01'
DEFAULT_TZ_NAME = 'Europe/Berlin'


# =============================================================================

if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
