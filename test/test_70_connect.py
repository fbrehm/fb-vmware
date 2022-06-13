#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 Frank Brehm, Berlin
@license: GPL3
@summary: test script (and module) for unit tests on module fb_vmware.connect
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
from general import SimpleTestObject

LOG = logging.getLogger('test-connection')


# =============================================================================
class TestVsphereConnection(FbVMWareTestcase):

    # -------------------------------------------------------------------------
    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    def test_import(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing import of fb_vmware.connect ...")
        import fb_vmware.connect
        from fb_vmware import VsphereConnection                          # noqa

        LOG.debug("Version of fb_vmware.connect: {!r}.".format(fb_vmware.connect.__version__))

    # -------------------------------------------------------------------------
    def test_init_object(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing init of a VsphereConnection object ...")

        from fb_vmware import VsphereConnection
        from fb_vmware.errors import VSphereNameError
        from fb_vmware.config import VSPhereConfigInfo

        my_vsphere_host = 'my-vsphere.uhu-banane.de'
        my_vsphere_user = 'test.user'
        my_vsphere_passwd = 'test-password'
        my_vsphere_dc = 'mydc'

        connect_info = VSPhereConfigInfo(
            host=my_vsphere_host, user=my_vsphere_user, password=my_vsphere_passwd,
            dc=my_vsphere_dc, appname=self.appname, verbose=1, initialized=True)

        connect = VsphereConnection(
            connect_info=connect_info,
            appname=self.appname,
            verbose=1,
        )

        LOG.debug("VsphereConnection %r: {!r}".format(connect))
        LOG.debug("VsphereConnection %s:\n{}".format(connect))

        self.assertIsInstance(connect, VsphereConnection)
        self.assertEqual(connect.appname, self.appname)
        self.assertEqual(connect.verbose, 1)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVsphereConnection('test_import', verbose))
    suite.addTest(TestVsphereConnection('test_init_object', verbose))
    # suite.addTest(TestVsphereConnection('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
