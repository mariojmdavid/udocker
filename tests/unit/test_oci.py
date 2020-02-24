#!/usr/bin/env python
"""
udocker unit tests: OciLocalFileAPI
"""

from unittest import TestCase, main
from udocker.oci import OciLocalFileAPI
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


class OciLocalFileAPITestCase(TestCase):
    """Test OciLocalFileAPI()."""

    def setUp(self):
        str_local = 'udocker.container.localrepo.LocalRepository'
        self.lrepo = patch(str_local)
        self.local = self.lrepo.start()
        self.mock_lrepo = Mock()
        self.local.return_value = self.mock_lrepo

    def tearDown(self):
        self.lrepo.stop()

    # def test_01__init(self):
    #     """Test01 OciLocalFileAPI() constructor."""

    # def test_02__load_structure(self):
    #     """Test02 OciLocalFileAPI()._load_structure."""

    # def test_03__get_from_manifest(self):
    #     """Test03 OciLocalFileAPI()._get_from_manifest."""

    # def test_04__load_manifest(self):
    #     """Test04 OciLocalFileAPI()._load_manifest."""

    # def test_05__load_repositories(self):
    #     """Test05 OciLocalFileAPI()._load_repositories."""

    # def test_06__load_image_step2(self):
    #     """Test07 OciLocalFileAPI()._load_image_step2."""

    # def test_07_load(self):
    #     """Test07 OciLocalFileAPI().load."""
