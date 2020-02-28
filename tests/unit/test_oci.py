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

    @patch('udocker.oci.FileUtil.isdir')
    @patch('udocker.oci.os.listdir')
    @patch('udocker.container.localrepo.LocalRepository.load_json', autospec=True)
    def test_02__load_structure(self, mock_ljson, mock_oslist, mock_isdir):
        """Test02 OciLocalFileAPI()._load_structure."""
        mock_ljson.side_effect = [[], []]
        status = OciLocalFileAPI(self.local)._load_structure('tmpimg')
        self.assertEqual(status, {})

        out_res = {'repolayers': {},
                   'manifest': {},
                   'oci-layout': 'oci_lay1',
                   'index': 'idx1'}
        mock_ljson.side_effect = ['oci_lay1', 'idx1']
        mock_oslist.return_value = ['f1']
        mock_isdir.return_value = False
        status = OciLocalFileAPI(self.local)._load_structure('tmpimg')
        self.assertEqual(status, out_res)

        out_res = {'repolayers': {'f1:f2': {'layer_a': 'f1',
                                            'layer_f': 'tmpimg/blobs/f1/f2',
                                            'layer_h': 'f2'}},
                   'manifest': {},
                   'oci-layout': 'oci_lay1',
                   'index': 'idx1'}
        mock_ljson.side_effect = ['oci_lay1', 'idx1']
        mock_oslist.side_effect = [['f1'], ['f2']]
        mock_isdir.return_value = True
        status = OciLocalFileAPI(self.local)._load_structure('tmpimg')
        self.assertEqual(status, out_res)

    def test_03__get_from_manifest(self):
        """Test03 OciLocalFileAPI()._get_from_manifest."""
        imgtag = '123'
        struct = {'manifest': {'123': {'json': {'layers': [{'digest': 'd1'},
                                                           {'digest': 'd2'}],
                                                'config': {'digest': 'dgt'}}}}}
        lay_out = ['d2', 'd1']
        conf_out = 'dgt'
        status = OciLocalFileAPI(self.local)._get_from_manifest(struct, imgtag)
        self.assertEqual(status, (conf_out, lay_out))

    # def test_04__load_manifest(self):
    #     """Test04 OciLocalFileAPI()._load_manifest."""

    # def test_05__load_repositories(self):
    #     """Test05 OciLocalFileAPI()._load_repositories."""

    # def test_06__load_image_step2(self):
    #     """Test07 OciLocalFileAPI()._load_image_step2."""

    # def test_07_load(self):
    #     """Test07 OciLocalFileAPI().load."""
