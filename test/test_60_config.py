#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Test script (and module) for unit tests on module fb_vmware.config.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2024 Frank Brehm, Berlin
@license: GPL3
"""

import logging
import os
import sys
import textwrap
from pathlib import Path

try:
    import unittest2 as unittest
except ImportError:
    import unittest

libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(0, libdir)

from general import FbVMWareTestcase, get_arg_verbose, init_root_logger

LOG = logging.getLogger('test-config')


# =============================================================================
class TestVsphereConfig(FbVMWareTestcase):
    """Testcase for unit tests on VmwareConfiguration objects."""

    # -------------------------------------------------------------------------
    def setUp(self):
        """Execute this on seting up before calling each particular test method."""
        super(TestVsphereConfig, self).setUp()

        self.test_dir = Path(__file__).parent.resolve()
        self.base_dir = self.test_dir.parent
        self.test_cfg_dir = self.test_dir / 'test-config'
        self._appname = 'test-config'

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Tear down routine for calling each particular test method."""
        pass

    # -------------------------------------------------------------------------
    def test_import(self):
        """Test import of fb_vmware.config."""
        LOG.info(self.get_method_doc())

        import fb_vmware.config
        LOG.debug('Version of fb_vmware.config: ' + fb_vmware.config.__version__)

        LOG.info('Testing import of VmwareConfigError from fb_vmware.config ...')
        from fb_vmware.config import VmwareConfigError
        doc = textwrap.dedent(VmwareConfigError.__doc__)
        LOG.debug('Description of VmwareConfigError: ' + doc)

        LOG.info('Testing import of VmwareConfiguration from fb_vmware.config ...')
        from fb_vmware.config import VmwareConfiguration
        doc = textwrap.dedent(VmwareConfiguration.__doc__)
        LOG.debug('Description of VmwareConfiguration: ' + doc)

    # -------------------------------------------------------------------------
    def test_object(self):
        """Test init of a VmwareConfiguration object."""
        LOG.info(self.get_method_doc())

        from fb_vmware.config import VmwareConfiguration

        cfg = VmwareConfiguration(
            appname=self.appname,
            config_dir='test', additional_stems='test',
            verbose=self.verbose,
        )
        LOG.debug('VmwareConfiguration %%r: %r', cfg)
        LOG.debug('VmwareConfiguration %%s: %s', str(cfg))

    # -------------------------------------------------------------------------
    def test_read_config(self):
        """Test reading of config."""
        LOG.info(self.get_method_doc())

        from fb_vmware.config import VmwareConfiguration

        cfg = VmwareConfiguration(
            appname=self.appname,
            config_dir='test', additional_stems='test',
            verbose=self.verbose,
        )
        cfg.read()
        cfg.eval()
        LOG.debug('VmwareConfiguration %%s: %s', str(cfg))


# =============================================================================
if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    LOG.info('Starting tests ...')

    suite = unittest.TestSuite()

    suite.addTest(TestVsphereConfig('test_import', verbose))
    suite.addTest(TestVsphereConfig('test_object', verbose))
    suite.addTest(TestVsphereConfig('test_read_config', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)


# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
