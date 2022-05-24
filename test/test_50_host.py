#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 Frank Brehm, Berlin
@license: GPL3
@summary: test script (and module) for unit tests on module fb_vmware.host
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

LOG = logging.getLogger('test-host')


# =============================================================================
class TestVmwareHost(FbVMWareTestcase):

    # -------------------------------------------------------------------------
    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    def test_import(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing import of fb_vmware.host ...")
        import fb_vmware.host
        from fb_vmware import VsphereHostBiosInfo                    # noqa
        from fb_vmware import VsphereHost                            # noqa

        LOG.debug("Version of fb_vmware.host: {!r}.".format(fb_vmware.host.__version__))

    # -------------------------------------------------------------------------
    def test_init_object(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing init of a VsphereHost object ...")

        from fb_vmware import VsphereHost
        from fb_vmware.errors import VSphereNameError

        with self.assertRaises((VSphereNameError, TypeError))  as cm:

            host = VsphereHost(appname=self.appname)
            LOG.debug("VsphereHost %s:\n{}".format(host))

        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        host_name = 'my-vmware-host'

        host = VsphereHost(
            name=host_name,
            appname=self.appname,
            verbose=1,
        )

        LOG.debug("VsphereHost %r: {!r}".format(host))
        LOG.debug("VsphereHost %s:\n{}".format(host))

        self.assertIsInstance(host, VsphereHost)
        self.assertEqual(host.appname, self.appname)
        self.assertEqual(host.verbose, 1)
        self.assertEqual(host.name, host_name)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVmwareHost('test_import', verbose))
    suite.addTest(TestVmwareHost('test_init_object', verbose))
    # suite.addTest(TestVmwareHost('test_init_from_summary', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
