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
import ssl

from abc import ABCMeta, abstractmethod

# Third party modules
from six import add_metaclass

import pytz

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

from fb_tools.common import to_bool
from fb_tools.handling_obj import HandlingObject

# Own modules
from .xlate import XLATOR

from .errors import BaseVSphereHandlerError
from .errors import VSphereCannotConnectError, VSphereVimFault

from .config import VSPhereConfigInfo, DEFAULT_VSPHERE_CLUSTER

__version__ = '0.2.4'

LOG = logging.getLogger(__name__)

_ = XLATOR.gettext

DEFAULT_TZ_NAME = 'Europe/Berlin'
DEFAULT_MAX_SEARCH_DEPTH = 10


# =============================================================================
@add_metaclass(ABCMeta)
class BaseVsphereHandler(HandlingObject):
    """
    Base class for a VSphere handler object.
    May not be instantiated.
    """

    max_search_depth = DEFAULT_MAX_SEARCH_DEPTH

    # -------------------------------------------------------------------------
    def __init__(
        self, connect_info, appname=None, verbose=0, version=__version__, base_dir=None,
            cluster=DEFAULT_VSPHERE_CLUSTER, auto_close=False, simulate=None,
            force=None, terminal_has_colors=False, initialized=False, tz=DEFAULT_TZ_NAME):

        self._cluster = cluster
        self._auto_close = False
        self._tz = pytz.timezone(DEFAULT_TZ_NAME)

        self.connect_info = None
        self.service_instance = None

        super(BaseVsphereHandler, self).__init__(
            appname=appname, verbose=verbose, version=version, base_dir=base_dir,
            simulate=simulate, force=force, terminal_has_colors=terminal_has_colors,
            initialized=False,
        )

        if not isinstance(connect_info, VSPhereConfigInfo):
            msg = _("The given parameter {pc!r} ({pv!r}) is not a {o} object.").format(
                pc='connect_info', pv=connect_info, o='VSPhereConfigInfo')
            raise BaseVSphereHandlerError(msg)

        if not connect_info.host:
            msg = _("No VSPhere host name or address given in {w}.").format(w='connect_info')
            raise BaseVSphereHandlerError(msg)

        if not connect_info.initialized:
            msg = _("The {c} object given as {w} is not initialized.").format(
                c='VSPhereConfigInfo', w='connect_info')
            raise BaseVSphereHandlerError(msg)

        self.connect_info = connect_info

        self.tz = tz
        self.auto_close = auto_close

        self.initialized = initialized

    # -----------------------------------------------------------
    @property
    def auto_close(self):
        """Flage, whether an existing connection should be closed on
            destroying the current object."""
        return getattr(self, '_auto_close', False)

    @auto_close.setter
    def auto_close(self, value):
        self._auto_close = to_bool(value)

    # -----------------------------------------------------------
    @property
    def dc(self):
        """The name of the VSphere datacenter to use."""

        connect_info = getattr(self, 'connect_info', None)
        if connect_info:
            return connect_info.dc
        return None

    # -----------------------------------------------------------
    @property
    def cluster(self):
        """The name of the VSphere cluster to use."""
        return self._cluster

    # -----------------------------------------------------------
    @property
    def tz(self):
        """The current time zone."""
        return self._tz

    @tz.setter
    def tz(self, value):
        if isinstance(value, pytz.tzinfo.BaseTzInfo):
            self._tz = value
        else:
            self._tz = pytz.timezone(value)

    # -------------------------------------------------------------------------
    @abstractmethod
    def __repr__(self):
        """Typecasting into a string for reproduction."""

        out = "<%s()>" % (self.__class__.__name__)
        return out

    # -------------------------------------------------------------------------
    def _repr(self):

        out = "<%s(" % (self.__class__.__name__)

        fields = []
        fields.append("connect_info={}".format(self.connect_info._repr()))
        fields.append("cluster={!r}".format(self.cluster))
        fields.append("auto_close={!r}".format(self.auto_close))
        fields.append("simulate={!r}".format(self.simulate))
        fields.append("force={!r}".format(self.force))

        out += ", ".join(fields) + ")>"
        return out

    # -------------------------------------------------------------------------
    def as_dict(self, short=True):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(BaseVsphereHandler, self).as_dict(short=short)
        res['dc'] = self.dc
        res['tz'] = None
        if self.tz:
            res['tz'] = self.tz.zone
        res['cluster'] = self.cluster
        res['auto_close'] = self.auto_close
        res['max_search_depth'] = self.max_search_depth

        return res

    # -------------------------------------------------------------------------
    def connect(self):

        LOG.debug(_("Connecting to vSphere {!r} ...").format(self.connect_info.full_url))

        try:
            if self.connect_info.use_https:

                ssl_context = None
                if hasattr(ssl, '_create_unverified_context'):
                    ssl_context = ssl._create_unverified_context()

                self.service_instance = SmartConnect(
                    protocol='https', host=self.connect_info.host, port=self.connect_info.port,
                    user=self.connect_info.user, pwd=self.connect_info.password,
                    sslContext=ssl_context)

            else:

                self.service_instance = SmartConnect(
                    protocol='http', host=self.connect_info.host, port=self.connect_info.port,
                    user=self.connect_info.user, pwd=self.connect_info.password)

        except vim.fault.VimFault as e:
            raise VSphereVimFault(e, self.connect_info.full_url)

        if not self.service_instance:
            raise VSphereCannotConnectError(self.connect_info.url)

    # -------------------------------------------------------------------------
    def disconnect(self):

        if self.service_instance:
            LOG.debug(_("Disconnecting from VSPhere {!r}.").format(self.connect_info.url))
            Disconnect(self.service_instance)

        self.service_instance = None

    # -------------------------------------------------------------------------
    def get_obj(self, content, vimtype, name):

        obj = None
        container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
        for c in container.view:
            if c.name == name:
                obj = c
                break

        return obj

    # -------------------------------------------------------------------------
    def __del__(self):
        if self.auto_close:
            self.disconnect()


# =============================================================================

if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
