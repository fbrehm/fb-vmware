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

from .obj import VsphereObject, DEFAULT_OBJ_STATUS

from .about import VsphereAboutInfo

from .cluster import VsphereCluster

from .datastore import VsphereDatastore, VsphereDatastoreDict

from .ds_cluster import VsphereDsCluster, VsphereDsClusterDict

from .dc import VsphereDatacenter
from .dc import DEFAULT_HOST_FOLDER, DEFAULT_VM_FOLDER, DEFAULT_DS_FOLDER, DEFAULT_NETWORK_FOLDER

from .controller import VsphereDiskController, VsphereDiskControllerList

from .disk import VsphereDisk, VsphereDiskList

from .ether import VsphereEthernetcard, VsphereEthernetcardList

from .network import VsphereNetwork, VsphereNetworkDict

from .host_port_group import VsphereHostPortgroup, VsphereHostPortgroupList

from .host import VsphereHostBiosInfo, VsphereHost, VsphereHostList

# from .vm import VsphereVm, VsphereVmList

__version__ = '0.3.3'

LOG = logging.getLogger(__name__)

_ = XLATOR.gettext


# =============================================================================

if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
