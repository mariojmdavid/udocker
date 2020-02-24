#!/usr/bin/env python
"""
udocker unit tests: LocalFileAPI
"""

from unittest import TestCase, main
import ctypes
from udocker.localfile import LocalFileAPI
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class LocalFileAPITestCase(TestCase):
    """Test LocalFileAPI()."""

    def setUp(self):
        pass

    def tearDown(self):
        pass
