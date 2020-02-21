#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
udocker unit tests: HostInfo
"""
from unittest import TestCase, main
from udocker.helper.hostinfo import HostInfo
from udocker.config import Config
from udocker.container.localrepo import LocalRepository
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class HostInfoTestCase(TestCase):
    """Test HostInfo"""

    def setUp(self):
        Config().getconf()
        self.local = LocalRepository()

    def tearDown(self):
        pass
