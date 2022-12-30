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

from .base import BaseVsphereHandler                                            # noqa
from .base import DEFAULT_MAX_SEARCH_DEPTH, DEFAULT_TZ_NAME                     # noqa

from .obj import VsphereObject, DEFAULT_OBJ_STATUS                              # noqa

from .about import VsphereAboutInfo                                             # noqa

from .cluster import VsphereCluster                                             # noqa

from .datastore import VsphereDatastore, VsphereDatastoreDict                   # noqa

from .ds_cluster import VsphereDsCluster, VsphereDsClusterDict                  # noqa

from .dc import VsphereDatacenter                                               # noqa
from .dc import DEFAULT_HOST_FOLDER, DEFAULT_VM_FOLDER                          # noqa
from .dc import DEFAULT_DS_FOLDER, DEFAULT_NETWORK_FOLDER                       # noqa

from .controller import VsphereDiskController, VsphereDiskControllerList        # noqa

from .disk import VsphereDisk, VsphereDiskList                                  # noqa

from .ether import VsphereEthernetcard, VsphereEthernetcardList                 # noqa

from .iface import VsphereVmInterface                                           # noqa

from .network import VsphereNetwork, VsphereNetworkDict                         # noqa

from .host_port_group import VsphereHostPortgroup, VsphereHostPortgroupList     # noqa

from .host import VsphereHostBiosInfo, VsphereHost, VsphereHostList             # noqa

from .vm import VsphereVm, VsphereVmList                                        # noqa

from .connect import VsphereConnection                                          # noqa
from .connect import DEFAULT_OS_VERSION, DEFAULT_VM_CFG_VERSION                 # noqa

from .config import VmwareConfigError, VmwareConfiguration                      # noqa
from .config import DEFAULT_CONFIG_DIR, DEFAULT_VSPHERE_PORT                    # noqa
from .config import DEFAULT_VSPHERE_USER, DEFAULT_VSPHERE_DC                    # noqa
from .config import DEFAULT_VSPHERE_CLUSTER                                     # noqa

__version__ = '0.5.6'

LOG = logging.getLogger(__name__)

_ = XLATOR.gettext


# =============================================================================

if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
