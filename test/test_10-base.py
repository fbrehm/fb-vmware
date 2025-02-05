#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Test script (and module) for unit tests on module fb_vmware.base.

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

LOG = logging.getLogger('test-base')


# =============================================================================
class TestVMWareBase(FbVMWareTestcase):
    """Testcase for unit tests on base object."""

    # -------------------------------------------------------------------------
    def setUp(self):
        """Execute this on seting up before calling each particular test method."""
        super(TestVMWareBase, self).setUp()

    # -------------------------------------------------------------------------
    def test_import(self):
        """Test importing of fb_vmware.base."""
        LOG.info(self.get_method_doc())

        import fb_vmware.base
        from fb_vmware import BaseVsphereHandler

        LOG.debug('Version of fb_vmware.base: {!r}.'.format(fb_vmware.base.__version__))

        doc = textwrap.dedent(BaseVsphereHandler.__doc__)
        LOG.debug('Description of BaseVsphereHandler: ' + doc)

    # -------------------------------------------------------------------------
    def test_init_base(self):
        """Test init of a BaseVsphereHandler object."""
        LOG.info(self.get_method_doc())

        from fb_vmware import BaseVsphereHandler
        from fb_vmware.config import VSPhereConfigInfo

        with self.assertRaises(TypeError) as cm:
            gen_handler = BaseVsphereHandler()
            LOG.error('This should not be visible - version of BaseVsphereHandler: {!r}'.format(
                gen_handler.version))
        e = cm.exception
        LOG.debug('TypeError raised on instantiate a BaseVsphereHandler: %s', str(e))

        from fb_vmware import DEFAULT_MAX_SEARCH_DEPTH
        from fb_vmware import DEFAULT_VSPHERE_PORT, DEFAULT_TZ_NAME

        my_vsphere_host = 'my-vsphere.uhu-banane.de'
        my_vsphere_user = 'test.user'
        my_vsphere_passwd = 'test-password'
        my_vsphere_dc = 'mydc'

        connect_info = VSPhereConfigInfo(
            host=my_vsphere_host, user=my_vsphere_user, password=my_vsphere_passwd,
            dc=my_vsphere_dc, appname=self.appname, verbose=1, initialized=True)

        class TestVsphereHandler(BaseVsphereHandler):

            def __repr__(self):
                return self._repr()

        gen_handler = TestVsphereHandler(
            connect_info=connect_info,
            appname=self.appname,
            verbose=1,
        )
        LOG.debug('TestVsphereHandler %r: {!r}'.format(gen_handler))
        LOG.debug('TestVsphereHandler %s:\n{}'.format(gen_handler))

        self.assertIsInstance(gen_handler, BaseVsphereHandler)
        self.assertEqual(gen_handler.verbose, 1)
        self.assertEqual(gen_handler.connect_info.host, my_vsphere_host)
        self.assertEqual(gen_handler.connect_info.port, DEFAULT_VSPHERE_PORT)
        self.assertTrue(gen_handler.connect_info.use_https)
        self.assertEqual(gen_handler.connect_info.user, my_vsphere_user)
        self.assertEqual(gen_handler.connect_info.password, my_vsphere_passwd)
        self.assertEqual(gen_handler.connect_info.dc, my_vsphere_dc)
        self.assertEqual(gen_handler.tz.zone, DEFAULT_TZ_NAME)
        self.assertFalse(gen_handler.auto_close)
        self.assertEqual(gen_handler.max_search_depth, DEFAULT_MAX_SEARCH_DEPTH)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info('Starting tests ...')

    suite = unittest.TestSuite()

    suite.addTest(TestVMWareBase('test_import', verbose))
    suite.addTest(TestVMWareBase('test_init_base', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
