#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 Frank Brehm, Berlin
@license: GPL3
@summary: test script (and module) for unit tests on module fb_vmware.ds_cluster
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

LOG = logging.getLogger('test-ds-cluster')


# =============================================================================
class TestVDataStoreCluster(FbVMWareTestcase):

    # -------------------------------------------------------------------------
    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    def test_import(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing import of fb_vmware.ds_cluster ...")
        import fb_vmware.ds_cluster
        from fb_vmware import VsphereDsCluster                       # noqa
        from fb_vmware import VsphereDsClusterDict                   # noqa

        LOG.debug("Version of fb_vmware.ds_cluster: {!r}.".format(fb_vmware.ds_cluster.__version__))

    # -------------------------------------------------------------------------
    def test_init_object(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing init of a VsphereDsCluster object ...")

        from fb_vmware import VsphereDsCluster
        from fb_vmware.errors import VSphereNameError

        with self.assertRaises((VSphereNameError, TypeError))  as cm:

            dsc = VsphereDsCluster(appname=self.appname)
            LOG.debug("VsphereDsCluster %s:\n{}".format(dcc))

        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        ds_cluster_name = 'my-datastore-cluster'
        capacity = int(500 * 1024 * 1024 * 1024)
        free_space = int(capacity * 0.7)

        dsc = VsphereDsCluster(
            name=ds_cluster_name,
            appname=self.appname,
            capacity=capacity,
            free_space=free_space,
            verbose=1,
        )

        LOG.debug("VsphereDsCluster %r: {!r}".format(dsc))
        LOG.debug("VsphereDsCluster %s:\n{}".format(dsc))

        self.assertIsInstance(dsc, VsphereDsCluster)
        self.assertEqual(dsc.appname, self.appname)
        self.assertEqual(dsc.verbose, 1)
        self.assertEqual(dsc.name, ds_cluster_name)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVDataStoreCluster('test_import', verbose))
    suite.addTest(TestVDataStoreCluster('test_init_object', verbose))
    # suite.addTest(TestVDataStoreCluster('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
