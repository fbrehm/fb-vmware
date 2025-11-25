#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Test script (and module) for unit tests on module fb_vmware.iface.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2025 Frank Brehm, Berlin
@license: GPL3
"""

import logging
import os
import sys
import textwrap

try:
    import unittest2 as unittest
except ImportError:
    import unittest

libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, libdir)

from general import FbVMWareTestcase, get_arg_verbose, init_root_logger

LOG = logging.getLogger("test-iface")


# =============================================================================
class TestVInterface(FbVMWareTestcase):
    """Testcase for unit tests on a VsphereVmInterface object."""

    # -------------------------------------------------------------------------
    def setUp(self):
        """Execute this on seting up before calling each particular test method."""
        super(TestVInterface, self).setUp()

    # -------------------------------------------------------------------------
    def test_import(self):
        """Test import of fb_vmware.iface."""
        LOG.info(self.get_method_doc())

        import fb_vmware.iface
        from fb_vmware import VsphereVmInterface

        LOG.debug("Version of fb_vmware.iface: {!r}.".format(fb_vmware.iface.__version__))

        doc = textwrap.dedent(VsphereVmInterface.__doc__)
        LOG.debug("Description of VsphereVmInterface: " + doc)

    # -------------------------------------------------------------------------
    def test_init_object(self):
        """Test nit of a VsphereVmInterface object."""
        LOG.info(self.get_method_doc())

        from fb_vmware import VsphereVmInterface

        iface_name = "iface0"
        nw_name = "10.12.11.0_24"

        iface = VsphereVmInterface(
            name=iface_name,
            network_name=nw_name,
            appname=self.appname,
            verbose=1,
        )

        LOG.debug("VsphereVmInterface %r: {!r}".format(iface))
        LOG.debug("VsphereVmInterface %s:\n{}".format(iface))

        self.assertIsInstance(iface, VsphereVmInterface)
        self.assertEqual(iface.appname, self.appname)
        self.assertEqual(iface.verbose, 1)


# =============================================================================
if __name__ == "__main__":

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVInterface("test_import", verbose))
    suite.addTest(TestVInterface("test_init_object", verbose))
    # suite.addTest(TestVInterface('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
