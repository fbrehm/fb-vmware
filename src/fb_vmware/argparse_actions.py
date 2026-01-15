"""
@summary: A module containing some useful argparse actions.

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2026 by Frank Brehm, Berlin
"""

from __future__ import absolute_import

# Standard modules
import argparse
import logging
# import os
# from pathlib import Path

# Third party modules
# from fb_tools.common import is_sequence

# Own modules
from .xlate import XLATOR

__version__ = "0.1.1"
LOG = logging.getLogger(__name__)

_ = XLATOR.gettext


# =============================================================================
class NonNegativeIntegerOptionAction(argparse.Action):
    """
    It's an argparse action class to ensure a positive integer value.

    It ensures, that the given value is an integer value, which ist greater or equal to 0.
    """

    # -------------------------------------------------------------------------
    def __init__(self, option_strings, may_zero=True, *args, **kwargs):
        """Initialize the NonNegativeIntegerOptionAction object."""
        self.may_zero = bool(may_zero)

        super(NonNegativeIntegerOptionAction, self).__init__(
            *args, **kwargs, option_strings=option_strings,
        )

    # -------------------------------------------------------------------------
    def __call__(self, parser, namespace, value, option_string=None):
        """Check the given value from command line for type and the valid range."""
        try:
            val = int(value)
        except Exception as e:
            msg = _("Got a {c} for converting {v!r} into an integer value: {e}").format(
                c=e.__class__.__name__, v=value, e=e
            )
            raise argparse.ArgumentError(self, msg)

        if val < 0:
            msg = _("The option must not be negative (given: {}).").format(value)
            raise argparse.ArgumentError(self, msg)

        if not self.may_zero and val == 0:
            msg = _("The option must not be zero.")
            raise argparse.ArgumentError(self, msg)

        setattr(namespace, self.dest, val)


# =============================================================================
if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
