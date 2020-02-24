#!/usr/bin/env python
"""
udocker unit tests: Unshare
"""

from unittest import TestCase, main
import ctypes
from udocker.helper.unshare import Unshare
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class UnshareTestCase(TestCase):
    """Test Unshare()."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('udocker.helper.unshare.ctypes.CDLL')
    def test_01_unshare(self, mock_cdll):
        """Test01 Unshare().unshare"""
        status = Unshare().unshare(False)
        self.assertTrue(mock_cdll.return_value.unshare.called)
        self.assertTrue(status)
        # TODO test for flag = True

    # def test_02_namespace_exec(self):
    #     """Test02 Unshare().namespace_exec"""


if __name__ == '__main__':
    main()
