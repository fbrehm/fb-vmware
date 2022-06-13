#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 Frank Brehm, Berlin
@license: GPL3
@summary: test script (and module) for unit tests on error (exception) classes
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

LOG = logging.getLogger('test-errors')


# =============================================================================
class TestVMWareErrors(FbVMWareTestcase):

    # -------------------------------------------------------------------------
    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    def test_import(self):

        if self.verbose >= 1:
            print()
        LOG.info("Testing import of fb_vmware.errors ...")
        import fb_vmware.errors
        from fb_vmware.errors import VSphereHandlerError        # noqa

        LOG.debug("Version of fb_vmware.errors: {!r}.".format(fb_vmware.errors.__version__))

    # -------------------------------------------------------------------------
    def test_vsphere_error(self):

        if self.verbose >= 1:
            print()
        LOG.info("Test raising a VSphereHandlerError exception ...")

        from fb_vmware.errors import VSphereHandlerError, VSphereExpectedError

        err_msg = "Bla blub"

        with self.assertRaises(VSphereHandlerError) as cm:
            raise VSphereHandlerError(err_msg)
        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)
        self.assertEqual(str(e), err_msg)

        with self.assertRaises(VSphereHandlerError) as cm:
            raise VSphereExpectedError(err_msg)
        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)
        self.assertEqual(str(e), err_msg)

    # -------------------------------------------------------------------------
    def test_nodatastore_error(self):

        if self.verbose >= 1:
            print()
        LOG.info("Test raising a VSphereNoDatastoresFoundError exception ...")

        from fb_vmware.errors import VSphereNoDatastoresFoundError

        with self.assertRaises(VSphereNoDatastoresFoundError) as cm:
            raise VSphereNoDatastoresFoundError()
        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        err_msg = "Bla blub"
        with self.assertRaises(VSphereNoDatastoresFoundError) as cm:
            raise VSphereNoDatastoresFoundError(err_msg)
        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)
        self.assertEqual(str(e), err_msg)

    # -------------------------------------------------------------------------
    def test_name_error(self):

        if self.verbose >= 1:
            print()
        LOG.info("Test raising a VSphereNameError exception ...")

        wrong_obj = 3
        wrong_obj_type = wrong_obj.__class__.__qualname__
        correct_obj_type = 'BaseVsphereHandler'

        from fb_vmware.errors import VSphereHandlerError, VSphereNameError

        with self.assertRaises(VSphereHandlerError) as cm:
            raise VSphereNameError(wrong_obj_type)
        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        with self.assertRaises(VSphereHandlerError) as cm:
            raise VSphereNameError(wrong_obj_type, correct_obj_type)
        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

    # -------------------------------------------------------------------------
    def test_notfound_error(self):

        if self.verbose >= 1:
            print()

        from fb_vmware.errors import VSphereHandlerError

        LOG.info("Test raising a VSphereDatacenterNotFoundError exception ...")

        from fb_vmware.errors import VSphereDatacenterNotFoundError

        with self.assertRaises(TypeError) as cm:
            raise VSphereDatacenterNotFoundError()
        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        with self.assertRaises(VSphereHandlerError) as cm:
            raise VSphereDatacenterNotFoundError('my-dc')
        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)
        self.assertIsInstance(e, VSphereDatacenterNotFoundError)

        LOG.info("Test raising a VSphereVmNotFoundError exception ...")

        from fb_vmware.errors import VSphereVmNotFoundError

        with self.assertRaises(TypeError) as cm:
            raise VSphereVmNotFoundError()
        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        with self.assertRaises(VSphereHandlerError) as cm:
            raise VSphereVmNotFoundError('my-VM')
        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)
        self.assertIsInstance(e, VSphereVmNotFoundError)

        LOG.info("Test raising a VSphereNoDatastoreFoundError exception ...")

        from fb_vmware.errors import VSphereNoDatastoreFoundError

        with self.assertRaises(TypeError) as cm:
            raise VSphereNoDatastoreFoundError()
        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        with self.assertRaises(ValueError) as cm:
            raise VSphereNoDatastoreFoundError('my-datastore')
        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        with self.assertRaises(VSphereHandlerError) as cm:
            raise VSphereNoDatastoreFoundError(20 * 1024 * 1024 * 1024)
        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)
        self.assertIsInstance(e, VSphereNoDatastoreFoundError)

        LOG.info("Test raising a VSphereNetworkNotExistingError exception ...")

        from fb_vmware.errors import VSphereNetworkNotExistingError

        with self.assertRaises(TypeError) as cm:
            raise VSphereNetworkNotExistingError()
        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        with self.assertRaises(VSphereHandlerError) as cm:
            raise VSphereNetworkNotExistingError('my-network')
        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)
        self.assertIsInstance(e, VSphereNetworkNotExistingError)

    # -------------------------------------------------------------------------
    def test_misc_errors(self):

        if self.verbose >= 1:
            print()

        from fb_vmware.errors import VSphereHandlerError, VSphereExpectedError

        LOG.info("Test raising a VSphereCannotConnectError exception ...")

        from fb_vmware.errors import VSphereCannotConnectError

        wrong_params_list = (
            [], ['test-vca.nowhere.net', 9100], ['test-vca.nowhere.net', 9100, 'admin', 'blub'])
        for wrong_params in wrong_params_list:
            with self.assertRaises(TypeError) as cm:
                raise VSphereCannotConnectError(*wrong_params)
            e = cm.exception
            LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        good_params = ['test-vca.nowhere.net']
        with self.assertRaises(VSphereHandlerError) as cm:
            raise VSphereCannotConnectError(*good_params)
        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)
        self.assertIsInstance(e, VSphereCannotConnectError)

        LOG.info("Test raising a TimeoutCreateVmError exception ...")

        from fb_vmware.errors import TimeoutCreateVmError

        wrong_params_list = ([], ['my-VM', 3600, 'blub'], ['my-VM', 'uhu'])

        for wrong_params in wrong_params_list:
            with self.assertRaises((TypeError, ValueError)) as cm:
                raise TimeoutCreateVmError(*wrong_params)
            e = cm.exception
            LOG.debug("%s raised: %s", e.__class__.__qualname__, e)

        good_params_list = (['my-VM', 3600], ['my-VM'], ['my-VM', None])

        for good_params in good_params_list:

            with self.assertRaises(VSphereHandlerError) as cm:
                raise TimeoutCreateVmError(*good_params)
            e = cm.exception
            LOG.debug("%s raised: %s", e.__class__.__qualname__, e)
            self.assertIsInstance(e, TimeoutCreateVmError)


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVMWareErrors('test_import', verbose))
    suite.addTest(TestVMWareErrors('test_vsphere_error', verbose))
    suite.addTest(TestVMWareErrors('test_nodatastore_error', verbose))
    suite.addTest(TestVMWareErrors('test_name_error', verbose))
    suite.addTest(TestVMWareErrors('test_notfound_error', verbose))
    suite.addTest(TestVMWareErrors('test_misc_errors', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
