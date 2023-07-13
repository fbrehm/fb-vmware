#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: Module for for a Spinner class.

          A Spinner object is displaying on console a rotating or somehow
          other animated character during its existence.

          This class was taken from https://github.com/Tagar/stuff

          Example usage:

                from fb_vmware.spinner import Spinner

                with Spinner("just waiting a bit.. "):
                    time.sleep(3)

@author: Frank Brehm
@contact: frank@brehm-online.com
@copyright: © 2023 by Frank Brehm, Berlin
"""

import itertools
import sys
import threading
import time

__version__ = '1.0.1'


# =============================================================================
class Spinner(object):
    """Displaying  on console a rotating or somehow other animated character."""

        cycle_list = ['-', '/', '|', '\\']

    # -------------------------------------------------------------------------
    def __init__(self, message, delay=0.1, cycle_list=None):
        """Initialize a Spinner object."""
        _cycle_list = cycle_list
        if not cycle_list:
            _cycle_list = self.cycle_list
        self.spinner = itertools.cycle(_cycle_list)
        self.delay = delay
        self.busy = False
        self.spinner_visible = False
        sys.stdout.write(message)

    # -------------------------------------------------------------------------
    def write_next(self):
        """Write the next character from the cycle array on the current screen position."""
        with self._screen_lock:
            if not self.spinner_visible:
                sys.stdout.write(next(self.spinner))
                self.spinner_visible = True
                sys.stdout.flush()

    # -------------------------------------------------------------------------
    def remove_spinner(self, cleanup=False):
        """
        Remove the last visible cycle character from screen.

        If the parameter cleanup is true, then the screen cursor will be mnoved to the next line.
        """
        with self._screen_lock:
            if self.spinner_visible:
                sys.stdout.write('\b')
                self.spinner_visible = False
                if cleanup:
                    sys.stdout.write(' ')       # overwrite spinner with blank
                    sys.stdout.write('\r')      # move to next line
                sys.stdout.flush()

    # -------------------------------------------------------------------------
    def spinner_task(self):
        """Entry point of the Thread. It is an infinite loop."""
        while self.busy:
            self.write_next()
            time.sleep(self.delay)
            self.remove_spinner()

    # -------------------------------------------------------------------------
    def __enter__(self):
        """Execute this ction, when this object will be created for the with-block."""
        if sys.stdout.isatty():
            self._screen_lock = threading.Lock()
            self.busy = True
            self.thread = threading.Thread(target=self.spinner_task)
            self.thread.start()

    # -------------------------------------------------------------------------
    def __exit__(self, exc_type, exc_val, exc_traceback):
        """Exit action at the end of the with-block."""
        if sys.stdout.isatty():
            self.busy = False
            self.remove_spinner(cleanup=True)
        else:
            sys.stdout.write('\r')


# =============================================================================
if __name__ == '__main__':

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 list
