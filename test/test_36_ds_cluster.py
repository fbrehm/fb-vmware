#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Test script (and module) for unit tests on module fb_vmware.ds_cluster.

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

libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, libdir)

from general import FbVMWareTestcase, get_arg_verbose, init_root_logger

LOG = logging.getLogger("test-ds-cluster")


# =============================================================================
class TestVDataStoreCluster(FbVMWareTestcase):
    """Testcase for unit tests on a VsphereDsCluster object."""

    # -------------------------------------------------------------------------
    def setUp(self):
        """Execute this on seting up before calling each particular test method."""
        super(TestVDataStoreCluster, self).setUp()

    # -------------------------------------------------------------------------
    def test_import(self):
        """Test import of fb_vmware.ds_cluster."""
        LOG.info(self.get_method_doc())

        import fb_vmware.ds_cluster
        from fb_vmware import VsphereDsCluster
        from fb_vmware import VsphereDsClusterDict

        LOG.debug(
            "Version of fb_vmware.ds_cluster: {!r}.".format(fb_vmware.ds_cluster.__version__)
        )

        doc = textwrap.dedent(VsphereDsCluster.__doc__)
        LOG.debug("Description of VsphereDsCluster: " + doc)

        doc = textwrap.dedent(VsphereDsClusterDict.__doc__)
        LOG.debug("Description of VsphereDsClusterDict: " + doc)

    # -------------------------------------------------------------------------
    def test_init_object(self):
        """Test init of a VsphereDsCluster object."""
        LOG.info(self.get_method_doc())

        from fb_vmware import VsphereDsCluster
        from fb_vmware.errors import VSphereNameError

        with self.assertRaises((VSphereNameError, TypeError)) as cm:

            dsc = VsphereDsCluster(appname=self.appname)
            LOG.debug("VsphereDsCluster %s:\n{}".format(dsc))

        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        ds_cluster_name = "my-datastore-cluster"
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
if __name__ == "__main__":

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVDataStoreCluster("test_import", verbose))
    suite.addTest(TestVDataStoreCluster("test_init_object", verbose))
    # suite.addTest(TestVDataStoreCluster('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
