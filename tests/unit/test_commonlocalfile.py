#!/usr/bin/env python
"""
udocker unit tests: CommonLocalFileApi
"""

import sys
from unittest import TestCase, main
from udocker.commonlocalfile import CommonLocalFileApi
try:
    from unittest.mock import Mock, MagicMock, patch, mock_open
except ImportError:
    from mock import Mock, MagicMock, patch, mock_open

sys.path.append('.')


class CommonLocalFileApiTestCase(TestCase):
    """Test CommonLocalFileApi()."""

    def setUp(self):
        str_local = 'udocker.container.localrepo.LocalRepository'
        self.lrepo = patch(str_local)
        self.local = self.lrepo.start()
        self.mock_lrepo = Mock()
        self.local.return_value = self.mock_lrepo

    def tearDown(self):
        self.lrepo.stop()

    def test_01_init(self):
        """Test01 CommonLocalFileApi() constructor"""
        clfapi = CommonLocalFileApi(self.local)
        self.assertEqual(clfapi.localrepo, self.local)

    @patch('udocker.commonlocalfile.FileUtil.copyto')
    @patch('udocker.commonlocalfile.os.rename')
    def test_02__move_layer_to_v1repo(self, mock_rename, mock_copy):
        """Test02 CommonLocalFileApi()._move_layer_to_v1repo()."""
        layer_id = "xxx"
        filepath = "yy"
        self.local.layersdir = "/home/.udocker"
        clfapi = CommonLocalFileApi(self.local)
        status = clfapi._move_layer_to_v1repo(filepath, layer_id)
        self.assertFalse(status)

        layer_id = "12345"
        filepath = "/home/.udocker/12345.json"
        self.local.layersdir = "/home/.udocker"
        mock_rename.return_value = None
        mock_copy.return_value = True
        self.local.add_image_layer.return_value = True
        clfapi = CommonLocalFileApi(self.local)
        status = clfapi._move_layer_to_v1repo(filepath, layer_id)
        self.assertTrue(status)
        self.assertTrue(mock_rename.called)
        self.assertTrue(self.local.add_image_layer.called)

        layer_id = "12345"
        filepath = "/home/.udocker/12345.layer.tar"
        self.local.layersdir = "/home/.udocker"
        mock_rename.return_value = None
        mock_copy.return_value = True
        self.local.add_image_layer.return_value = True
        clfapi = CommonLocalFileApi(self.local)
        status = clfapi._move_layer_to_v1repo(filepath, layer_id)
        self.assertTrue(status)
        self.assertTrue(mock_rename.called)
        self.assertTrue(self.local.add_image_layer.called)

    # def test_03__load_image_step2(self):
    #     """Test03 CommonLocalFileApi()._load_image_step2()."""

    def test_04__load_image(self):
        """Test04 CommonLocalFileApi()._load_image()."""
        structure = "12345"
        imagerepo = "/home/.udocker/images"
        tag = "v1"
        self.local.cd_imagerepo.return_value = True
        clfapi = CommonLocalFileApi(self.local)
        status = clfapi._load_image(structure, imagerepo, tag)
        self.assertEqual(status, [])

        self.local.cd_imagerepo.return_value = False
        self.local.setup_imagerepo.return_value = True
        self.local.setup_tag.return_value = False
        clfapi = CommonLocalFileApi(self.local)
        status = clfapi._load_image(structure, imagerepo, tag)
        self.assertEqual(status, [])

        self.local.cd_imagerepo.return_value = False
        self.local.setup_imagerepo.return_value = True
        self.local.setup_tag.return_value = True
        self.local.set_version.return_value = False
        clfapi = CommonLocalFileApi(self.local)
        status = clfapi._load_image(structure, imagerepo, tag)
        self.assertEqual(status, [])

        self.local.cd_imagerepo.return_value = False
        self.local.setup_imagerepo.return_value = True
        self.local.setup_tag.return_value = True
        self.local.set_version.return_value = True
        clfapi = CommonLocalFileApi(self.local)
        status = clfapi._load_image(structure, imagerepo, tag)
        self.assertEqual(status, None)

    @patch('udocker.commonlocalfile.Uprocess.call')
    def test_05__untar_saved_container(self, mock_ucall):
        """Test05 CommonLocalFileApi()._untar_saved_container()."""
        tarfile = "file.tar"
        destdir = "/home/.udocker/images"
        mock_ucall.return_value = True
        clfapi = CommonLocalFileApi(self.local)
        status = clfapi._untar_saved_container(tarfile, destdir)
        self.assertFalse(status)

        mock_ucall.return_value = False
        clfapi = CommonLocalFileApi(self.local)
        status = clfapi._untar_saved_container(tarfile, destdir)
        self.assertTrue(status)

    # def test_06_create_container_meta(self):
    #     """Test06 CommonLocalFileApi().create_container_meta()."""

    # def test_07_import_toimage(self):
    #     """Test07 CommonLocalFileApi().import_toimage()."""

    # def test_08_import_tocontainer(self):
    #     """Test08 CommonLocalFileApi().import_tocontainer()."""

    # def test_09_import_clone(self):
    #     """Test09 CommonLocalFileApi().import_clone()."""

    # def test_10_clone_container(self):
    #     """Test10 CommonLocalFileApi().clone_container()."""

    @patch('udocker.commonlocalfile.os.path.exists')
    def test_11__get_imagedir_type(self, mock_exists):
        """Test11 CommonLocalFileApi()._get_imagedir_type()."""
        tmp_imagedir = "/home/.udocker/images/myimg"
        mock_exists.side_effect = [False, False]
        clfapi = CommonLocalFileApi(self.local)
        status = clfapi._get_imagedir_type(tmp_imagedir)
        self.assertEqual(status, "")

        mock_exists.side_effect = [True, False]
        clfapi = CommonLocalFileApi(self.local)
        status = clfapi._get_imagedir_type(tmp_imagedir)
        self.assertEqual(status, "OCI")

        mock_exists.side_effect = [False, True]
        clfapi = CommonLocalFileApi(self.local)
        status = clfapi._get_imagedir_type(tmp_imagedir)
        self.assertEqual(status, "Docker")

if __name__ == '__main__':
    main()
