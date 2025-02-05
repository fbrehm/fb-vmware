#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Test script (and module) for unit tests on module fb_vmware.vm.

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

LOG = logging.getLogger('test-vm')


# =============================================================================
class TestVsphereVM(FbVMWareTestcase):
    """Testcase for unit tests on VsphereVm and VsphereVmList objects."""

    # -------------------------------------------------------------------------
    def setUp(self):
        """Execute this on seting up before calling each particular test method."""
        super(TestVsphereVM, self).setUp()

    # -------------------------------------------------------------------------
    def test_import(self):
        """Test import of fb_vmware.vm."""
        LOG.info(self.get_method_doc())

        import fb_vmware.vm
        from fb_vmware import VsphereVm
        from fb_vmware import VsphereVmList

        LOG.debug('Version of fb_vmware.vm: {!r}.'.format(fb_vmware.vm.__version__))

        doc = textwrap.dedent(VsphereVm.__doc__)
        LOG.debug('Description of VsphereVm: ' + doc)

        doc = textwrap.dedent(VsphereVmList.__doc__)
        LOG.debug('Description of VsphereVmList: ' + doc)

    # -------------------------------------------------------------------------
    def test_init_object(self):
        """Test init of a VsphereVm object."""
        LOG.info(self.get_method_doc())

        from fb_vmware import VsphereVm
        from fb_vmware.errors import VSphereNameError

        with self.assertRaises((VSphereNameError, TypeError)) as cm:

            vm = VsphereVm(appname=self.appname)
            LOG.debug('VsphereVm %s:\n{}'.format(vm))

        e = cm.exception
        LOG.debug('%s raised: %s', e.__class__.__qualname__, e)

        vm_name = 'my-vmware-vm'

        vm = VsphereVm(
            name=vm_name,
            appname=self.appname,
            verbose=1,
        )

        LOG.debug('VsphereVm %r: {!r}'.format(vm))
        LOG.debug('VsphereVm %s:\n{}'.format(vm))

        self.assertIsInstance(vm, VsphereVm)
        self.assertEqual(vm.appname, self.appname)
        self.assertEqual(vm.verbose, 1)
        self.assertEqual(vm.name, vm_name)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info('Starting tests ...')

    suite = unittest.TestSuite()

    suite.addTest(TestVsphereVM('test_import', verbose))
    suite.addTest(TestVsphereVM('test_init_object', verbose))
    # suite.addTest(TestVsphereVM('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
