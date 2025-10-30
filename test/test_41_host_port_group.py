#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Test script (and module) for unit tests on module fb_vmware.host_port_group.

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

LOG = logging.getLogger('test-host-port-group')


# =============================================================================
class TestVHostPortGroup(FbVMWareTestcase):
    """Testcase for unit tests on a VsphereHostPortgroup object."""

    # -------------------------------------------------------------------------
    def setUp(self):
        """Execute this on seting up before calling each particular test method."""
        super(TestVHostPortGroup, self).setUp()

    # -------------------------------------------------------------------------
    def test_import(self):
        """Test import of fb_vmware.host_port_group."""
        LOG.info(self.get_method_doc())

        import fb_vmware.host_port_group
        from fb_vmware import VsphereHostPortgroup
        from fb_vmware import VsphereHostPortgroupList

        LOG.debug('Version of fb_vmware.host_port_group: {!r}.'.format(
            fb_vmware.host_port_group.__version__))

        doc = textwrap.dedent(VsphereHostPortgroup.__doc__)
        LOG.debug('Description of VsphereHostPortgroup: ' + doc)

        doc = textwrap.dedent(VsphereHostPortgroupList.__doc__)
        LOG.debug('Description of VsphereHostPortgroupList: ' + doc)

    # -------------------------------------------------------------------------
    def test_init_object(self):
        """Test init of a VsphereHostPortgroup object."""
        LOG.info(self.get_method_doc())

        from fb_vmware import VsphereHostPortgroup

        group = VsphereHostPortgroup(
            appname=self.appname,
            verbose=1,
        )

        LOG.debug('VsphereHostPortgroup %r: {!r}'.format(group))
        LOG.debug('VsphereHostPortgroup %s:\n{}'.format(group))

        self.assertIsInstance(group, VsphereHostPortgroup)
        self.assertEqual(group.appname, self.appname)
        self.assertEqual(group.verbose, 1)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info('Starting tests ...')

    suite = unittest.TestSuite()

    suite.addTest(TestVHostPortGroup('test_import', verbose))
    suite.addTest(TestVHostPortGroup('test_init_object', verbose))
    # suite.addTest(TestVHostPortGroup('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
