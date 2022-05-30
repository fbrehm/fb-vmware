#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 Frank Brehm, Berlin
@license: GPL3
@summary: test script (and module) for unit tests on module fb_vmware.server
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

LOG = logging.getLogger('test-server')


# =============================================================================
class TestVsphereServer(FbVMWareTestcase):

    # -------------------------------------------------------------------------
    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    def test_import(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing import of fb_vmware.server ...")
        import fb_vmware.server
        from fb_vmware import VsphereServer                          # noqa

        LOG.debug("Version of fb_vmware.server: {!r}.".format(fb_vmware.server.__version__))

    # -------------------------------------------------------------------------
    def test_init_object(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing init of a VsphereServer object ...")

        from fb_vmware import VsphereServer
        from fb_vmware.errors import VSphereNameError

        server = VsphereServer(
            appname=self.appname,
            verbose=1,
        )

        LOG.debug("VsphereServer %r: {!r}".format(server))
        LOG.debug("VsphereServer %s:\n{}".format(server))

        self.assertIsInstance(server, VsphereServer)
        self.assertEqual(server.appname, self.appname)
        self.assertEqual(server.verbose, 1)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVsphereServer('test_import', verbose))
    suite.addTest(TestVsphereServer('test_init_object', verbose))
    # suite.addTest(TestVsphereServer('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4