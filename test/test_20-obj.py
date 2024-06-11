#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Test script (and module) for unit tests on module fb_vmware.obj.

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

LOG = logging.getLogger('test-object')


# =============================================================================
class TestVMWareObject(FbVMWareTestcase):
    """Testcase for unit tests on a VsphereObject."""

    # -------------------------------------------------------------------------
    def setUp(self):
        """Execute this on seting up before calling each particular test method."""
        if self.verbose >= 1:
            print()

    # -------------------------------------------------------------------------
    def test_import(self):
        """Test import of fb_vmware.obj."""
        LOG.info(self.get_method_doc())

        import fb_vmware.obj
        from fb_vmware import VsphereObject

        LOG.debug('Version of fb_vmware.obj: {!r}.'.format(fb_vmware.obj.__version__))
        LOG.debug('Description of VsphereObject: ' + textwrap.dedent(VsphereObject.__doc__))

    # -------------------------------------------------------------------------
    def test_init_object(self):
        """Test init of a VsphereObject object."""
        LOG.info(self.get_method_doc())

        from fb_vmware import VsphereObject, DEFAULT_OBJ_STATUS
        obj_type = 'testobject'
        obj_name = 'Test-Object'

        gen_obj = VsphereObject(
            name=obj_name,
            obj_type=obj_type,
            appname=self.appname,
            verbose=1,
        )

        LOG.debug('VsphereObject %r: {!r}'.format(gen_obj))
        LOG.debug('VsphereObject %s:\n{}'.format(gen_obj))

        self.assertIsInstance(gen_obj, VsphereObject)
        self.assertEqual(gen_obj.verbose, 1)
        self.assertEqual(gen_obj.name, obj_name)
        self.assertEqual(gen_obj.obj_type, obj_type)
        self.assertEqual(gen_obj.config_status, DEFAULT_OBJ_STATUS)
        self.assertEqual(gen_obj.status, DEFAULT_OBJ_STATUS)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info('Starting tests ...')

    suite = unittest.TestSuite()

    suite.addTest(TestVMWareObject('test_import', verbose))
    suite.addTest(TestVMWareObject('test_init_object', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
