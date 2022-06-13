#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 Frank Brehm, Berlin
@license: GPL3
@summary: test script (and module) for unit tests on module fb_vmware.iface
'''

import os
import sys
import logging

try:
    import unittest2 as unittest
except ImportError:
    import unittest

libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(0, libdir)

from general import FbVMWareTestcase, get_arg_verbose, init_root_logger
from general import SimpleTestObject

LOG = logging.getLogger('test-iface')


# =============================================================================
class TestVInterface(FbVMWareTestcase):

    # -------------------------------------------------------------------------
    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    def test_import(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing import of fb_vmware.iface ...")
        import fb_vmware.iface
        from fb_vmware import VsphereVmInterface                     # noqa

        LOG.debug("Version of fb_vmware.iface: {!r}.".format(fb_vmware.iface.__version__))

    # -------------------------------------------------------------------------
    def test_init_object(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing init of a VsphereVmInterface object ...")

        from fb_vmware import VsphereVmInterface
        from fb_vmware.errors import VSphereNameError

        iface_name = 'iface0'
        nw_name = '10.12.11.0_24'

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
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVInterface('test_import', verbose))
    suite.addTest(TestVInterface('test_init_object', verbose))
    # suite.addTest(TestVInterface('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
