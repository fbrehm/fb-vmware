#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Test script (and module) for unit tests on module fb_vmware.host.

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

libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, libdir)

from general import FbVMWareTestcase, get_arg_verbose, init_root_logger

LOG = logging.getLogger('test-host')


# =============================================================================
class TestVmwareHost(FbVMWareTestcase):
    """Testcase for unit tests on VsphereHostBiosInfo and VsphereHost objects."""

    # -------------------------------------------------------------------------
    def setUp(self):
        """Execute this on seting up before calling each particular test method."""
        super(TestVmwareHost, self).setUp()

    # -------------------------------------------------------------------------
    def test_import(self):
        """Test import of fb_vmware.host."""
        LOG.info(self.get_method_doc())

        import fb_vmware.host
        from fb_vmware import VsphereHostBiosInfo
        from fb_vmware import VsphereHost

        LOG.debug('Version of fb_vmware.host: {!r}.'.format(fb_vmware.host.__version__))

        doc = textwrap.dedent(VsphereHostBiosInfo.__doc__)
        LOG.debug('Description of VsphereHostBiosInfo: ' + doc)

        doc = textwrap.dedent(VsphereHost.__doc__)
        LOG.debug('Description of VsphereHost: ' + doc)

    # -------------------------------------------------------------------------
    def test_init_object(self):
        """Test init of a VsphereHost object."""
        LOG.info(self.get_method_doc())

        from fb_vmware import VsphereHost
        from fb_vmware.errors import VSphereNameError

        with self.assertRaises((VSphereNameError, TypeError)) as cm:

            host = VsphereHost(appname=self.appname)
            LOG.debug('VsphereHost %s:\n{}'.format(host))

        e = cm.exception
        LOG.debug('%s raised: %s', e.__class__.__qualname__, e)

        host_name = 'my-vmware-host'

        host = VsphereHost(
            name=host_name,
            appname=self.appname,
            verbose=1,
        )

        LOG.debug('VsphereHost %r: {!r}'.format(host))
        LOG.debug('VsphereHost %s:\n{}'.format(host))

        self.assertIsInstance(host, VsphereHost)
        self.assertEqual(host.appname, self.appname)
        self.assertEqual(host.verbose, 1)
        self.assertEqual(host.name, host_name)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info('Starting tests ...')

    suite = unittest.TestSuite()

    suite.addTest(TestVmwareHost('test_import', verbose))
    suite.addTest(TestVmwareHost('test_init_object', verbose))
    # suite.addTest(TestVmwareHost('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
