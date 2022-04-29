#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 Frank Brehm, Berlin
@license: GPL3
@summary: test script (and module) for unit tests on module fb_vmware.about
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

LOG = logging.getLogger('test-aboutinfo')


# =============================================================================
class TestVMAboutInfo(FbVMWareTestcase):

    # -------------------------------------------------------------------------
    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    def test_import(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing import of fb_vmware.about ...")
        import fb_vmware.about
        from fb_vmware import VsphereAboutInfo                     # noqa

        LOG.debug("Version of fb_vmware.about: {!r}.".format(fb_vmware.about.__version__))

    # -------------------------------------------------------------------------
    def test_init_object(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing init of a VsphereAboutInfo object ...")

        from fb_vmware import VsphereAboutInfo

        about_info = VsphereAboutInfo(
            appname=self.appname,
            verbose=1,
        )

        LOG.debug("VsphereAboutInfo %r: {!r}".format(about_info))
        LOG.debug("VsphereAboutInfo %s:\n{}".format(about_info))

        self.assertIsInstance(about_info, VsphereAboutInfo)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVMAboutInfo('test_import', verbose))
    suite.addTest(TestVMAboutInfo('test_init_object', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
