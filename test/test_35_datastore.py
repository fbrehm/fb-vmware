#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Test script (and module) for unit tests on module fb_vmware.datastore.

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

from fb_tools.common import pp

libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, libdir)

from general import FbVMWareTestcase, get_arg_verbose, init_root_logger

LOG = logging.getLogger("test-datastore")


# =============================================================================
class TestVDataStore(FbVMWareTestcase):
    """Testcase for unit tests on a VsphereDatastore object."""

    # -------------------------------------------------------------------------
    def setUp(self):
        """Execute this on seting up before calling each particular test method."""
        super(TestVDataStore, self).setUp()

    # -------------------------------------------------------------------------
    def test_import(self):
        """Test import of fb_vmware.datastore."""
        LOG.info(self.get_method_doc())

        import fb_vmware.datastore
        from fb_vmware import VsphereDatastore
        from fb_vmware import VsphereDatastoreDict

        LOG.debug("Version of fb_vmware.datastore: {!r}.".format(fb_vmware.datastore.__version__))

        doc = textwrap.dedent(VsphereDatastore.__doc__)
        LOG.debug("Description of VsphereDatastore: " + doc)

        doc = textwrap.dedent(VsphereDatastoreDict.__doc__)
        LOG.debug("Description of VsphereDatastoreDict: " + doc)

    # -------------------------------------------------------------------------
    def test_init_object(self):
        """Test init of a VsphereDatastore object."""
        LOG.info(self.get_method_doc())

        from fb_vmware import VsphereDatastore
        from fb_vmware.errors import VSphereNameError

        with self.assertRaises((VSphereNameError, TypeError)) as cm:

            ds = VsphereDatastore(appname=self.appname)
            LOG.debug("VsphereDatastore %s:\n{}".format(ds))

        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        ds_name = "my-datastore"
        capacity = int(100 * 1024 * 1024 * 1024)
        free_space = int(capacity * 0.6)
        vsphere = "live"
        dc = "dc1"
        cluster = "StorageCluster1"

        ds = VsphereDatastore(
            name=ds_name,
            appname=self.appname,
            capacity=capacity,
            free_space=free_space,
            vsphere=vsphere,
            dc_name=dc,
            cluster=cluster,
            verbose=1,
        )

        LOG.debug("VsphereDatastore %r: {!r}".format(ds))
        LOG.debug("VsphereDatastore %s:\n{}".format(ds))

        self.assertIsInstance(ds, VsphereDatastore)
        self.assertEqual(ds.appname, self.appname)
        self.assertEqual(ds.verbose, 1)
        self.assertEqual(ds.name, ds_name)
        self.assertEqual(ds.vsphere, vsphere)
        self.assertEqual(ds.dc_name, dc)
        self.assertEqual(ds.cluster, cluster)

    # -------------------------------------------------------------------------
    def test_valid_search_chains(self):
        """Test valid search chains of a VsphereDatastoreDict."""
        LOG.info(self.get_method_doc())

        expected_chains = ("any", "hdd", "hdd-first", "ssd", "ssd-first")
        expected_chains_w_local = ("any", "hdd", "hdd-first", "local", "local-first", "ssd", "ssd-first")

        from fb_vmware import VsphereDatastoreDict

        LOG.debug("Expected search chains w/o storage type 'local': " + pp(expected_chains))
        LOG.debug("Expected search chains with storage type 'local': " + pp(expected_chains_w_local))

        got_chains = VsphereDatastoreDict.valid_search_chains()
        LOG.debug("Got search chains w/o storage type 'local': " + pp(got_chains))
        self.assertEqual(got_chains, expected_chains)

        got_chains = VsphereDatastoreDict.valid_search_chains(use_local=True)
        LOG.debug("Got search chains with storage type 'local': " + pp(got_chains))
        self.assertEqual(got_chains, expected_chains_w_local)


# =============================================================================
if __name__ == "__main__":

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVDataStore("test_import", verbose))
    suite.addTest(TestVDataStore("test_init_object", verbose))
    # suite.addTest(TestVDataStore('test_init_from_summary', verbose))
    suite.addTest(TestVDataStore("test_valid_search_chains", verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
