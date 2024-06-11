#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Test script (and module) for unit tests on module fb_vmware.controller.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2024 Frank Brehm, Berlin
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

LOG = logging.getLogger('test-controller')


# =============================================================================
class TestVController(FbVMWareTestcase):
    """Testcase for unit tests on a VsphereDiskController object."""

    # -------------------------------------------------------------------------
    def setUp(self):
        """Execute this on seting up before calling each particular test method."""
        if self.verbose >= 1:
            print()

    # -------------------------------------------------------------------------
    def test_import(self):
        """Test import of fb_vmware.controller."""
        LOG.info(self.get_method_doc())

        import fb_vmware.controller
        from fb_vmware import VsphereDiskController
        from fb_vmware import VsphereDiskControllerList

        LOG.debug('Version of fb_vmware.controller: {!r}.'.format(fb_vmware.controller.__version__))
        LOG.debug('Description of VsphereDiskController: ' + textwrap.dedent(VsphereDiskController.__doc__))
        doc = textwrap.dedent(VsphereDiskControllerList.__doc__)
        LOG.debug('Description of VsphereDiskControllerList: ' + doc)

    # -------------------------------------------------------------------------
    def test_init_object(self):
        """Test init of a VsphereDiskController object."""
        LOG.info(self.get_method_doc())

        from fb_vmware import VsphereDiskController

        controller = VsphereDiskController(
            appname=self.appname,
            verbose=1,
        )

        LOG.debug('VsphereDiskController %r: {!r}'.format(controller))
        LOG.debug('VsphereDiskController %s:\n{}'.format(controller))

        self.assertIsInstance(controller, VsphereDiskController)
        self.assertEqual(controller.appname, self.appname)
        self.assertEqual(controller.verbose, 1)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info('Starting tests ...')

    suite = unittest.TestSuite()

    suite.addTest(TestVController('test_import', verbose))
    suite.addTest(TestVController('test_init_object', verbose))
    # suite.addTest(TestVController('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
