#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 Frank Brehm, Berlin
@license: GPL3
@summary: test script (and module) for unit tests on module fb_vmware.disk
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

LOG = logging.getLogger('test-disk')


# =============================================================================
class TestVdisk(FbVMWareTestcase):

    # -------------------------------------------------------------------------
    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    def test_import(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing import of fb_vmware.disk ...")
        import fb_vmware.disk
        from fb_vmware import VsphereDisk                       # noqa
        from fb_vmware import VsphereDiskList                   # noqa

        LOG.debug("Version of fb_vmware.disk: {!r}.".format(fb_vmware.disk.__version__))

    # -------------------------------------------------------------------------
    def test_init_object(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing init of a VsphereDisk object ...")

        from fb_vmware import VsphereDisk

        capacity = int(50 * 1024 * 1024 * 1024)

        disk = VsphereDisk(
            appname=self.appname,
            verbose=1,
            size=capacity,
        )

        LOG.debug("VsphereDisk %r: {!r}".format(disk))
        LOG.debug("VsphereDisk %s:\n{}".format(disk))

        self.assertIsInstance(disk, VsphereDisk)
        self.assertEqual(disk.appname, self.appname)
        self.assertEqual(disk.verbose, 1)
        self.assertEqual(disk.size, capacity)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVdisk('test_import', verbose))
    suite.addTest(TestVdisk('test_init_object', verbose))
    # suite.addTest(TestVdisk('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
