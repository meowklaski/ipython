# encoding: utf-8
"""
Tests for testing.tools
"""

#-----------------------------------------------------------------------------
#  Copyright (C) 2008-2011  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import unittest

from IPython.testing import tools as tt

#-----------------------------------------------------------------------------
# Tests
#-----------------------------------------------------------------------------

class Test_ipexec_validate(unittest.TestCase, tt.TempFileMixin):

    def test_exception_path(self):
        """Test exception path in exception_validate.
        """
        self.mktmp("from __future__ import print_function\n"
                   "import sys\n"
                   "print('A')\n"
                   "print('B')\n"
                   )
        out = "A\nB"
        tt.ipexec_validate(self.fname, expected_out=out)

    def tearDown(self):
        # tear down correctly the mixin,
        # unittest.TestCase.tearDown does nothing
        tt.TempFileMixin.tearDown(self)
