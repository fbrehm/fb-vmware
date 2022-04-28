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

from .base import BaseVsphereHandler
from .base import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_USER
from .base import DEFAULT_DC, DEFAULT_CLUSTER, DEFAULT_TZ_NAME
from .base import DEFAULT_MAX_SEARCH_DEPTH

from .obj import VsphereObject

__version__ = '0.2.1'

LOG = logging.getLogger(__name__)

_ = XLATOR.gettext


# =============================================================================

if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
