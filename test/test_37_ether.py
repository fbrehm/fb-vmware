#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 Frank Brehm, Berlin
@license: GPL3
@summary: test script (and module) for unit tests on module fb_vmware.ether
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

LOG = logging.getLogger('test-ether')


# =============================================================================
class TestVEthernet(FbVMWareTestcase):

    # -------------------------------------------------------------------------
    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    def test_import(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing import of fb_vmware.ether ...")
        import fb_vmware.ether
        from fb_vmware import VsphereEthernetcard                    # noqa
        from fb_vmware import VsphereEthernetcardList                # noqa

        LOG.debug("Version of fb_vmware.ether: {!r}.".format(fb_vmware.ether.__version__))

    # -------------------------------------------------------------------------
    def test_init_object(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing init of a VsphereEthernetcard object ...")

        from fb_vmware import VsphereEthernetcard
        from fb_vmware.errors import VSphereNameError

        ether = VsphereEthernetcard(
            appname=self.appname,
            verbose=1,
        )

        LOG.debug("VsphereEthernetcard %r: {!r}".format(ether))
        LOG.debug("VsphereEthernetcard %s:\n{}".format(ether))

        self.assertIsInstance(ether, VsphereEthernetcard)
        self.assertEqual(ether.appname, self.appname)
        self.assertEqual(ether.verbose, 1)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVEthernet('test_import', verbose))
    suite.addTest(TestVEthernet('test_init_object', verbose))
    # suite.addTest(TestVEthernet('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
