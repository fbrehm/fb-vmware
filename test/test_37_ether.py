#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Test script (and module) for unit tests on module fb_vmware.ether.

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

LOG = logging.getLogger('test-ether')


# =============================================================================
class TestVEthernet(FbVMWareTestcase):
    """Testcase for unit tests on a VsphereEthernetcard object."""

    # -------------------------------------------------------------------------
    def setUp(self):
        """Execute this on seting up before calling each particular test method."""
        if self.verbose >= 1:
            print()

    # -------------------------------------------------------------------------
    def test_import(self):
        """Test import of fb_vmware.ether."""
        LOG.info(self.get_method_doc())

        import fb_vmware.ether
        from fb_vmware import VsphereEthernetcard
        from fb_vmware import VsphereEthernetcardList

        LOG.debug('Version of fb_vmware.ether: {!r}.'.format(fb_vmware.ether.__version__))
        LOG.debug('Description of VsphereEthernetcard: ' + textwrap.dedent(VsphereEthernetcard.__doc__))
        LOG.debug(
            'Description of VsphereEthernetcardList: ' + textwrap.dedent(VsphereEthernetcardList.__doc__))

    # -------------------------------------------------------------------------
    def test_init_object(self):
        """Test init of a VsphereEthernetcard object."""
        LOG.info(self.get_method_doc())

        from fb_vmware import VsphereEthernetcard

        ether = VsphereEthernetcard(
            appname=self.appname,
            verbose=1,
        )

        LOG.debug('VsphereEthernetcard %r: {!r}'.format(ether))
        LOG.debug('VsphereEthernetcard %s:\n{}'.format(ether))

        self.assertIsInstance(ether, VsphereEthernetcard)
        self.assertEqual(ether.appname, self.appname)
        self.assertEqual(ether.verbose, 1)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info('Starting tests ...')

    suite = unittest.TestSuite()

    suite.addTest(TestVEthernet('test_import', verbose))
    suite.addTest(TestVEthernet('test_init_object', verbose))
    # suite.addTest(TestVEthernet('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
