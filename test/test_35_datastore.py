#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 Frank Brehm, Berlin
@license: GPL3
@summary: test script (and module) for unit tests on module fb_vmware.datastore
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

LOG = logging.getLogger('test-datastore')


# =============================================================================
class TestVDataStore(FbVMWareTestcase):

    # -------------------------------------------------------------------------
    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    def test_import(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing import of fb_vmware.datastore ...")
        import fb_vmware.datastore
        from fb_vmware import VsphereDatastore                       # noqa
        from fb_vmware import VsphereDatastoreDict                   # noqa

        LOG.debug("Version of fb_vmware.datastore: {!r}.".format(fb_vmware.datastore.__version__))

    # -------------------------------------------------------------------------
    def test_init_object(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing init of a VsphereDatastore object ...")

        from fb_vmware import VsphereDatastore
        from fb_vmware.errors import VSphereNameError

        with self.assertRaises((VSphereNameError, TypeError))  as cm:

            ds = VsphereDatastore(appname=self.appname)
            LOG.debug("VsphereDatastore %s:\n{}".format(dc))

        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        ds_name = 'my-datastore'
        capacity = int(100 * 1024 * 1024 * 1024)
        free_space = int(capacity * 0.6)

        ds = VsphereDatastore(
            name=ds_name,
            appname=self.appname,
            capacity=capacity,
            free_space=free_space,
            verbose=1,
        )

        LOG.debug("VsphereDatastore %r: {!r}".format(ds))
        LOG.debug("VsphereDatastore %s:\n{}".format(ds))

        self.assertIsInstance(ds, VsphereDatastore)
        self.assertEqual(ds.appname, self.appname)
        self.assertEqual(ds.verbose, 1)
        self.assertEqual(ds.name, ds_name)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVDataStore('test_import', verbose))
    suite.addTest(TestVDataStore('test_init_object', verbose))
    # suite.addTest(TestVDataStore('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
