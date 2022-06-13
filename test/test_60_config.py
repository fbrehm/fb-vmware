#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2022 Frank Brehm, Berlin
@license: GPL3
@summary: test script (and module) for unit tests on module fb_vmware.config
'''

import os
import sys
import logging

from pathlib import Path

try:
    import unittest2 as unittest
except ImportError:
    import unittest

libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(0, libdir)

from general import FbVMWareTestcase, get_arg_verbose, init_root_logger
from general import SimpleTestObject

LOG = logging.getLogger('test-config')


# =============================================================================
class TestVsphereConfig(FbVMWareTestcase):

    # -------------------------------------------------------------------------
    def setUp(self):

        self.test_dir = Path(__file__).parent.resolve()
        self.base_dir = self.test_dir.parent
        self.test_cfg_dir = self.test_dir / 'test-config'
        self._appname = 'test-config'

    # -------------------------------------------------------------------------
    def tearDown(self):

        pass

    # -------------------------------------------------------------------------
    def test_import(self):

        LOG.info("Testing import of fb_vmware.config ...")
        import fb_vmware.config
        LOG.debug(
            "Version of fb_vmware.config: " + fb_vmware.config.__version__)

        LOG.info("Testing import of VmwareConfigError from fb_vmware.config ...")
        from fb_vmware.config import VmwareConfigError                                  # noqa

        LOG.info("Testing import of VmwareConfiguration from fb_vmware.config ...")
        from fb_vmware.config import VmwareConfiguration                                # noqa

    # -------------------------------------------------------------------------
    def test_object(self):

        LOG.info("Testing init of a VmwareConfiguration object.")

        from fb_vmware.config import VmwareConfiguration

        cfg = VmwareConfiguration(
            appname=self.appname,
            config_dir='test', additional_stems='test',
            verbose=self.verbose,
        )
        LOG.debug("VmwareConfiguration %%r: %r", cfg)
        LOG.debug("VmwareConfiguration %%s: %s", str(cfg))

    # -------------------------------------------------------------------------
    def test_read_config(self):

        LOG.info("Testing reading of config.")

        from fb_vmware.config import VmwareConfiguration

        cfg = VmwareConfiguration(
            appname=self.appname,
            config_dir='test', additional_stems='test',
            verbose=self.verbose,
        )
        cfg.read()
        cfg.eval()
        LOG.debug("VmwareConfiguration %%s: %s", str(cfg))


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestVsphereConfig('test_import', verbose))
    suite.addTest(TestVsphereConfig('test_object', verbose))
    suite.addTest(TestVsphereConfig('test_read_config', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)


# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
