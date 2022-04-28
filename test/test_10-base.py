#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 Frank Brehm, Berlin
@license: GPL3
@summary: test script (and module) for unit tests on module fb_vmware.base
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

LOG = logging.getLogger('test-base')


# =============================================================================
class TestVMWareBase(FbVMWareTestcase):

    # -------------------------------------------------------------------------
    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    def test_import(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing import of fb_vmware.base ...")
        import fb_vmware.base
        from fb_vmware import BaseVsphereHandler                # noqa

        LOG.debug("Version of fb_vmware.base: {!r}.".format(fb_vmware.base.__version__))

    # -------------------------------------------------------------------------
    def test_init_base(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing init of a BaseVsphereHandler object ...")

        from fb_vmware import BaseVsphereHandler

        with self.assertRaises(TypeError) as cm:
            gen_handler = BaseVsphereHandler()
            LOG.error("This should not be visible - version of BaseVsphereHandler: {!r}".format(
                gen_handler.version))
        e = cm.exception
        LOG.debug("TypeError raised on instantiate a BaseVsphereHandler: %s", str(e))

        from fb_vmware import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_USER
        from fb_vmware import DEFAULT_DC, DEFAULT_CLUSTER, DEFAULT_TZ_NAME
        from fb_vmware import DEFAULT_MAX_SEARCH_DEPTH

        class TestVsphereHandler(BaseVsphereHandler):

            def __repr__(self):
                return self._repr()

        gen_handler = TestVsphereHandler(
            appname=self.appname,
            verbose=1,
        )
        LOG.debug("TestVsphereHandler %r: {!r}".format(gen_handler))
        LOG.debug("TestVsphereHandler %s:\n{}".format(gen_handler))

        self.assertIsInstance(gen_handler, BaseVsphereHandler)
        self.assertEqual(gen_handler.verbose, 1)
        self.assertEqual(gen_handler.host, DEFAULT_HOST)
        self.assertEqual(gen_handler.port, DEFAULT_PORT)
        self.assertEqual(gen_handler.user, DEFAULT_USER)
        self.assertEqual(gen_handler.dc, DEFAULT_DC)
        self.assertEqual(gen_handler.cluster, DEFAULT_CLUSTER)
        self.assertEqual(gen_handler.tz.zone, DEFAULT_TZ_NAME)
        self.assertIs(gen_handler.password, None)
        self.assertFalse(gen_handler.auto_close)
        self.assertEqual(gen_handler.max_search_depth, DEFAULT_MAX_SEARCH_DEPTH)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVMWareBase('test_import', verbose))
    suite.addTest(TestVMWareBase('test_init_base', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
