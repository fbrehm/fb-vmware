#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 Frank Brehm, Berlin
@license: GPL3
@summary: test script (and module) for unit tests on module fb_vmware.cluster
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

LOG = logging.getLogger('test-cluster')


# =============================================================================
class TestVMCluster(FbVMWareTestcase):

    # -------------------------------------------------------------------------
    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    def test_import(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing import of fb_vmware.cluster ...")
        import fb_vmware.cluster
        from fb_vmware import VsphereCluster                     # noqa

        LOG.debug("Version of fb_vmware.cluster: {!r}.".format(fb_vmware.cluster.__version__))

    # -------------------------------------------------------------------------
    def test_init_object(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing init of a VsphereCluster object ...")

        from fb_vmware import VsphereCluster
        from fb_vmware.errors import VSphereNameError

        with self.assertRaises(VSphereNameError)  as cm:

            cluster = VsphereCluster(appname=self.appname)
            LOG.debug("VsphereCluster %s:\n{}".format(cluster))

        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        cluster_name = 'my-cluster'

        cluster = VsphereCluster(
            name=cluster_name,
            appname=self.appname,
            verbose=1,
        )

        LOG.debug("VsphereCluster %r: {!r}".format(cluster))
        LOG.debug("VsphereCluster %s:\n{}".format(cluster))

        self.assertIsInstance(cluster, VsphereCluster)
        self.assertEqual(cluster.appname, self.appname)
        self.assertEqual(cluster.verbose, 1)
        self.assertEqual(cluster.name, cluster_name)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVMCluster('test_import', verbose))
    suite.addTest(TestVMCluster('test_init_object', verbose))
    # suite.addTest(TestVMCluster('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
