#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 Frank Brehm, Berlin
@license: GPL3
@summary: test script (and module) for unit tests on module fb_vmware.dc
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

LOG = logging.getLogger('test-dc')


# =============================================================================
class TestVMDatacenter(FbVMWareTestcase):

    # -------------------------------------------------------------------------
    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    def test_import(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing import of fb_vmware.dc ...")
        import fb_vmware.dc
        from fb_vmware import VsphereDatacenter                     # noqa

        LOG.debug("Version of fb_vmware.dc: {!r}.".format(fb_vmware.dc.__version__))

    # -------------------------------------------------------------------------
    def test_init_object(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing init of a VsphereDatacenter object ...")

        from fb_vmware import VsphereDatacenter
        from fb_vmware.errors import VSphereNameError

        with self.assertRaises(VSphereNameError)  as cm:

            dc = VsphereDatacenter(appname=self.appname)
            LOG.debug("VsphereDatacenter %s:\n{}".format(dc))

        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        dc_name = 'my-dc'

        dc = VsphereDatacenter(
            name=dc_name,
            appname=self.appname,
            verbose=1,
        )

        LOG.debug("VsphereDatacenter %r: {!r}".format(dc))
        LOG.debug("VsphereDatacenter %s:\n{}".format(dc))

        self.assertIsInstance(dc, VsphereDatacenter)
        self.assertEqual(dc.appname, self.appname)
        self.assertEqual(dc.verbose, 1)
        self.assertEqual(dc.name, dc_name)

    # -------------------------------------------------------------------------
    def test_init_from_summary(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing init by calling VsphereDatacenter.from_summary() ...")

        from fb_vmware import VsphereDatacenter
        from fb_vmware.dc import DEFAULT_HOST_FOLDER, DEFAULT_VM_FOLDER
        from fb_vmware.dc import DEFAULT_DS_FOLDER, DEFAULT_NETWORK_FOLDER

        dc_name = 'my-dc'

        data = SimpleTestObject()
        data.name = dc_name
        data.configStatus = 'gray'

        data.datastoreFolder = SimpleTestObject()
        data.datastoreFolder.name = DEFAULT_DS_FOLDER

        data.networkFolder = SimpleTestObject()
        data.networkFolder.name = DEFAULT_NETWORK_FOLDER

        data.hostFolder = SimpleTestObject()

        with self.assertRaises(TypeError)  as cm:

            dc = VsphereDatacenter.from_summary(
                data, appname=self.appname, verbose=self.verbose)
            LOG.debug("VsphereDatacenter %s:\n{}".format(dc))

        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        with self.assertRaises(AssertionError)  as cm:

            dc = VsphereDatacenter.from_summary(
                data, appname=self.appname, verbose=self.verbose, test_mode=True)
            LOG.debug("VsphereDatacenter %s:\n{}".format(dc))

        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        data.overallStatus = 'gray'

        data.hostFolder.name = DEFAULT_HOST_FOLDER

        data.vmFolder = SimpleTestObject()
        data.vmFolder.name = DEFAULT_VM_FOLDER

        dc = VsphereDatacenter.from_summary(
            data, appname=self.appname, verbose=self.verbose, test_mode=True)
        LOG.debug("VsphereDatacenter %s:\n{}".format(dc))


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVMDatacenter('test_import', verbose))
    suite.addTest(TestVMDatacenter('test_init_object', verbose))
    suite.addTest(TestVMDatacenter('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
