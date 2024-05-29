#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for special error classes on VSphere API operations.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2024 by Frank Brehm, Berlin
"""
from __future__ import absolute_import

# Standard modules

# Third party modules

from fb_tools.errors import FbHandlerError

# Own modules
from .xlate import XLATOR

__version__ = '1.0.0'

_ = XLATOR.gettext


# =============================================================================
class FbVMWareError(FbHandlerError):
    """Base class for all exception belonging to VSphere/VMWare."""

    pass


# =============================================================================
class BaseVSphereHandlerError(FbVMWareError):
    """Base class for all exception belonging to VSphere."""

    pass


# =============================================================================
class VSphereHandlerError(BaseVSphereHandlerError):
    """Base class for all exception belonging to VSphere."""

    pass


# =============================================================================
class VSphereNoDatastoresFoundError(FbHandlerError):
    """Special error class used, if no appropriate datastore could be found."""

    # -------------------------------------------------------------------------
    def __init__(self, msg=None):
        """Initialize the VSphereNoDatastoresFoundError object."""
        if not msg:
            msg = _('No VSphere datastores found.')
        self.msg = msg

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into a string."""
        return self.msg


# =============================================================================
class VSphereExpectedError(VSphereHandlerError):
    """
    Base class for all expected application errors.

    These are exceptions raised in application objects, which are
    displayed without stack trace.
    """

    pass


# =============================================================================
class VSphereNameError(VSphereExpectedError):
    """Special error class for invalid Vsphere object names."""

    # -------------------------------------------------------------------------
    def __init__(self, name, obj_type=None):
        """Initialize the VSphereNameError object."""
        self.name = name
        self.obj_type = obj_type

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into a string."""
        if self.obj_type:
            msg = _('Invalid name {n!r} for a {o} VSphere object.').format(
                n=self.name, o=self.obj_type)
        else:
            msg = _('Invalid name {!r} for a VSphere object.').format(self.name)

        return msg


# =============================================================================
class VSphereDatacenterNotFoundError(VSphereExpectedError):
    """Error class, if the given datacenter was not found in VSphere."""

    # -------------------------------------------------------------------------
    def __init__(self, dc):
        """Initialize the VSphereDatacenterNotFoundError object."""
        self.dc = dc

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into a string."""
        msg = _('The VSphere datacenter {!r} is not existing.').format(self.dc)
        return msg


# =============================================================================
class VSphereVmNotFoundError(VSphereExpectedError):
    """Special error class for the case, that the given VM was not found in VSphere."""

    # -------------------------------------------------------------------------
    def __init__(self, vm):
        """Initialize the VSphereVmNotFoundError object."""
        self.vm = vm

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into a string."""
        msg = _('The VSphere Virtual machine {!r} was not found.').format(self.vm)
        return msg


# =============================================================================
class VSphereNoDatastoreFoundError(VSphereExpectedError):
    """Error class for the case, if no SAN based data store was with enogh free space was found."""

    # -------------------------------------------------------------------------
    def __init__(self, needed_bytes):
        """Initialize the VSphereNoDatastoreFoundError object."""
        self.needed_bytes = int(needed_bytes)

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into a string."""
        mb = float(self.needed_bytes) / 1024.0 / 1024.0
        gb = mb / 1024.0

        msg = _(
            'No SAN based datastore found with at least {m:0.0f} MiB == {g:0.1f} GiB '
            'available space found.').format(m=mb, g=gb)
        return msg


# =============================================================================
class VSphereNetworkNotExistingError(VSphereExpectedError):
    """Special error class for the case, if the expected network is not existing."""

    # -------------------------------------------------------------------------
    def __init__(self, net_name):
        """Initialize the VSphereNetworkNotExistingError object."""
        self.net_name = net_name

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into a string."""
        msg = _('The network {!r} is not existing.').format(self.net_name)
        return msg


# =============================================================================
class VSphereCannotConnectError(VSphereExpectedError):
    """Error class, if it cannot connect to the given vSphere server."""

    # -------------------------------------------------------------------------
    def __init__(self, url):
        """Initialize the VSphereCannotConnectError object."""
        self.url = url

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into a string."""
        msg = _('Could not connect to the vSphere {!r}.').format(self.url)
        return msg

# =============================================================================
class VSphereVimFault(VSphereExpectedError):
    """Error class, if it cannot connect to vSphere and gets a vim.fault.VimFault."""

    # -------------------------------------------------------------------------
    def __init__(self, fault, url):
        """Initialize the VSphereVimFault object."""
        self.fault = fault
        self.url = url

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into a string."""
        msg = _('Got a {c} on connecting to vSphere {url!r}:').format(
            c=self.fault.__class__.__name__, url=self.url)
        msg += ' ' + self.fault.msg
        return msg


# =============================================================================
class TimeoutCreateVmError(VSphereExpectedError):
    """Exception when a timeout on creating a VM was reached."""

    # -------------------------------------------------------------------------
    def __init__(self, vm, timeout=None):
        """Initialize the TimeoutCreateVmError object."""
        t_o = None
        if timeout is not None:
            t_o = float(timeout)
        self.timeout = t_o

        self.vm = vm

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into a string."""
        if self.timeout is not None:
            msg = _('Timeout on creating VM {vm!r} after {to:0.1f} seconds.').format(
                vm=self.vm, to=self.timeout)
        else:
            msg = _('Timeout on creating VM {!r}.').format(self.vm)
        return msg


# =============================================================================
class WrongPortTypeError(FbVMWareError, TypeError):
    """Exception when wrong VSPhere server port was given."""

    # -------------------------------------------------------------------------
    def __init__(self, port, emesg=None):
        """Initialize the WrongPortTypeError object."""
        self.port = port
        self.emesg = emesg

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into a string."""
        msg = _('Invalid type of {!r} for a port of a VSPhere server').format(self.port)
        if self.emesg:
            msg += ': ' + self.emesg
        else:
            msg += '.'

        return msg

# =============================================================================
class WrongPortValueError(FbVMWareError, ValueError):
    """Exception when a wrong port number was given."""

    default_max_port = (2 ** 16) - 1

    # -------------------------------------------------------------------------
    def __init__(self, port, max_port=None):
        """Initialize the WrongPortValueError object."""
        self.port = port
        self.max_port = max_port
        if self.max_port is None:
            self.max_port = self.default_max_port

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecast into a string."""
        msg = _(
            'Invalid port number {port!r} for the VSphere server, '
            'PORT must be greater than zero and less or equal to {max}.').format(
            port=self.port, max=self.max_port)

        return msg


# =============================================================================
if __name__ == '__main__':

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
