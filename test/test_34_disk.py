#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Test script (and module) for unit tests on module fb_vmware.disk.

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

libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(0, libdir)

from general import FbVMWareTestcase, get_arg_verbose, init_root_logger

LOG = logging.getLogger('test-disk')


# =============================================================================
class TestVdisk(FbVMWareTestcase):
    """Testcase for unit tests on a VsphereDisk object."""

    # -------------------------------------------------------------------------
    def setUp(self):
        """Execute this on seting up before calling each particular test method."""
        super(TestVdisk, self).setUp()

    # -------------------------------------------------------------------------
    def test_import(self):
        """Test import of fb_vmware.disk."""
        LOG.info(self.get_method_doc())

        import fb_vmware.disk
        from fb_vmware import VsphereDisk
        from fb_vmware import VsphereDiskList

        LOG.debug('Version of fb_vmware.disk: {!r}.'.format(fb_vmware.disk.__version__))

        doc = textwrap.dedent(VsphereDisk.__doc__)
        LOG.debug('Description of VsphereDisk: ' + doc)

        doc = textwrap.dedent(VsphereDiskList.__doc__)
        LOG.debug('Description of VsphereDiskList: ' + doc)

    # -------------------------------------------------------------------------
    def test_init_object(self):
        """Test init of a VsphereDisk object."""
        LOG.info(self.get_method_doc())

        from fb_vmware import VsphereDisk

        capacity = int(50 * 1024 * 1024 * 1024)

        disk = VsphereDisk(
            appname=self.appname,
            verbose=1,
            size=capacity,
        )

        LOG.debug('VsphereDisk %r: {!r}'.format(disk))
        LOG.debug('VsphereDisk %s:\n{}'.format(disk))

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

    LOG.info('Starting tests ...')

    suite = unittest.TestSuite()

    suite.addTest(TestVdisk('test_import', verbose))
    suite.addTest(TestVdisk('test_init_object', verbose))
    # suite.addTest(TestVdisk('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
