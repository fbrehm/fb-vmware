#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for a base VSphere handler object.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2023 by Frank Brehm, Berlin
"""
# flake8: noqa
from __future__ import absolute_import

# Standard modules
import logging

# Own modules

from .about import VsphereAboutInfo
from .base import BaseVsphereHandler
from .base import DEFAULT_MAX_SEARCH_DEPTH, DEFAULT_TZ_NAME
from .cluster import VsphereCluster
from .config import DEFAULT_CONFIG_DIR, DEFAULT_VSPHERE_PORT
from .config import DEFAULT_VSPHERE_CLUSTER
from .config import DEFAULT_VSPHERE_DC, DEFAULT_VSPHERE_USER
from .config import VmwareConfigError, VmwareConfiguration
from .connect import DEFAULT_OS_VERSION, DEFAULT_VM_CFG_VERSION
from .connect import VsphereConnection
from .controller import VsphereDiskController, VsphereDiskControllerList
from .datastore import VsphereDatastore, VsphereDatastoreDict
from .dc import DEFAULT_DS_FOLDER
from .dc import DEFAULT_HOST_FOLDER
from .dc import DEFAULT_NETWORK_FOLDER
from .dc import DEFAULT_VM_FOLDER
from .dc import VsphereDatacenter
from .disk import VsphereDisk, VsphereDiskList
from .ds_cluster import VsphereDsCluster
from .ds_cluster import VsphereDsClusterDict
from .ether import VsphereEthernetcard
from .ether import VsphereEthernetcardList
from .host import VsphereHost
from .host import VsphereHostBiosInfo
from .host import VsphereHostList
from .host_port_group import VsphereHostPortgroup
from .host_port_group import VsphereHostPortgroupList
from .iface import VsphereVmInterface
from .network import VsphereNetwork
from .network import VsphereNetworkDict
from .obj import DEFAULT_OBJ_STATUS
from .obj import VsphereObject
from .vm import VsphereVm
from .vm import VsphereVmList
from .xlate import XLATOR


__version__ = '0.6.1'

LOG = logging.getLogger(__name__)

_ = XLATOR.gettext


# =============================================================================

if __name__ == '__main__':

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
