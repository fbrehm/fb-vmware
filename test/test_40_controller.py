#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Test script (and module) for unit tests on module fb_vmware.controller.

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

LOG = logging.getLogger("test-controller")


# =============================================================================
class TestVController(FbVMWareTestcase):
    """Testcase for unit tests on a VsphereDiskController object."""

    # -------------------------------------------------------------------------
    def setUp(self):
        """Execute this on seting up before calling each particular test method."""
        super(TestVController, self).setUp()

    # -------------------------------------------------------------------------
    def test_import(self):
        """Test import of fb_vmware.controller."""
        LOG.info(self.get_method_doc())

        import fb_vmware.controller
        from fb_vmware import VsphereDiskController
        from fb_vmware import VsphereDiskControllerList

        LOG.debug(
            "Version of fb_vmware.controller: {!r}.".format(fb_vmware.controller.__version__)
        )

        doc = textwrap.dedent(VsphereDiskController.__doc__)
        LOG.debug("Description of VsphereDiskController: " + doc)

        doc = textwrap.dedent(VsphereDiskControllerList.__doc__)
        LOG.debug("Description of VsphereDiskControllerList: " + doc)

    # -------------------------------------------------------------------------
    def test_init_object(self):
        """Test init of a VsphereDiskController object."""
        LOG.info(self.get_method_doc())

        from fb_vmware import VsphereDiskController

        controller = VsphereDiskController(
            appname=self.appname,
            verbose=1,
        )

        LOG.debug("VsphereDiskController %r: {!r}".format(controller))
        LOG.debug("VsphereDiskController %s:\n{}".format(controller))

        self.assertIsInstance(controller, VsphereDiskController)
        self.assertEqual(controller.appname, self.appname)
        self.assertEqual(controller.verbose, 1)

    # -------------------------------------------------------------------------
    def test_get_controller_class(self):
        """Test classmethod VsphereDiskController.get_disk_controller_class."""
        LOG.info(self.get_method_doc())

        from pyVmomi import vim
        from fb_vmware import VsphereDiskController
        from fb_vmware.errors import VSphereDiskCtrlrTypeNotFoudError

        LOG.debug("Test VsphereDiskController.get_disk_controller_class().")
        (cls, desc, type_name) = VsphereDiskController.get_disk_controller_class()
        LOG.debug("Got a {cls} class - {desc!r}".format(cls=cls.__name__, desc=desc))
        self.assertIs(cls, vim.vm.device.ParaVirtualSCSIController)
        self.assertEqual(type_name, VsphereDiskController.default_conroller_type)

        LOG.debug("Test VsphereDiskController.get_disk_controller_class('lsi_logic').")
        (cls, desc, type_name) = VsphereDiskController.get_disk_controller_class("lsi_logic")
        LOG.debug("Got a {cls} class - {desc!r}".format(cls=cls.__name__, desc=desc))
        self.assertIs(cls, vim.vm.device.VirtualLsiLogicController)

        with self.assertRaises(VSphereDiskCtrlrTypeNotFoudError) as cm:

            (cls, desc, type_name) = VsphereDiskController.get_disk_controller_class("uhu")
            LOG.debug("Got a {cls} class - {desc!r}".format(cls=cls.__name__, desc=desc))

        e = cm.exception
        LOG.debug("%s raised: %s", e.__class__.__qualname__, e)


# =============================================================================
if __name__ == "__main__":

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVController("test_import", verbose))
    suite.addTest(TestVController("test_init_object", verbose))
    suite.addTest(TestVController("test_get_controller_class", verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
