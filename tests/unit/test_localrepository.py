#!/usr/bin/env python
"""
udocker unit tests: LocalRepository
"""
import sys
import os
from unittest import TestCase, main
from udocker.container.localrepo import LocalRepository
from udocker.config import Config
try:
    from unittest.mock import patch, mock_open, call, Mock
except ImportError:
    from mock import patch, mock_open, call, Mock

try:
    from io import BytesIO as bytestr
except ImportError:
    from StringIO import StringIO as bytestr

if sys.version_info[0] >= 3:
    BUILTIN = "builtins"
else:
    BUILTIN = "__builtin__"

BOPEN = BUILTIN + '.open'
UDOCKER_TOPDIR = "/home/u1/.udocker"


class LocalRepositoryTestCase(TestCase):
    """Management of local repository of container
    images and extracted containers
    """

    def setUp(self):
        Config().getconf()
        Config().conf['topdir'] = UDOCKER_TOPDIR
        Config().conf['bindir'] = ""
        Config().conf['libdir'] = ""
        Config().conf['reposdir'] = ""
        Config().conf['layersdir'] = ""
        Config().conf['containersdir'] = ""
        Config().conf['homedir'] = "/home/u1"

        self.futilpatch = patch("udocker.utils.fileutil.FileUtil")
        self.futil = self.futilpatch.start()
        self.mock_futil = Mock()
        self.futil.return_value = self.mock_futil
        self.futil.return_value.register_prefix.side_effect = [None, None,
                                                               None]

    def tearDown(self):
        self.futil.stop()

    def test_01_init(self):
        """Test01 LocalRepository() constructor."""
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        self.assertTrue(lrepo.topdir)
        self.assertTrue(lrepo.reposdir)
        self.assertTrue(lrepo.layersdir)
        self.assertTrue(lrepo.containersdir)
        self.assertTrue(lrepo.bindir)
        self.assertTrue(lrepo.libdir)
        self.assertTrue(lrepo.homedir)
        self.assertEqual(lrepo.topdir, UDOCKER_TOPDIR)
        self.assertEqual(lrepo.cur_repodir, "")
        self.assertEqual(lrepo.cur_tagdir, "")
        self.assertEqual(lrepo.cur_containerdir, "")
        self.assertTrue(self.futil.register_prefix.called_count, 3)

    def test_02_setup(self):
        """Test02 LocalRepository().setup()."""
        newdir = "/home/u2/.udocker"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.setup(newdir)
        self.assertEqual(lrepo.topdir, newdir)

    @patch('udocker.container.localrepo.os.path.exists')
    @patch('udocker.container.localrepo.os.makedirs')
    def test_03_create_repo(self, mock_mkdir, mock_exists):
        """Test03 LocalRepository().create_repo()."""
        Config.conf['keystore'] = "tmp"
        mock_exists.side_effect = [False, False, False, False,
                                   False, False, False]
        mock_mkdir.side_effect = [None, None, None, None,
                                  None, None, None]
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.create_repo()
        self.assertTrue(status)
        self.assertTrue(mock_exists.call_count, 7)
        self.assertTrue(mock_mkdir.call_count, 7)

        Config.conf['keystore'] = "tmp"
        mock_exists.side_effect = OSError("fail")
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.create_repo()
        self.assertFalse(status)

    @patch('udocker.container.localrepo.os.path.exists')
    def test_04_is_repo(self, mock_exists):
        """Test04 LocalRepository().is_repo()."""
        mock_exists.side_effect = [False, True, False, False,
                                   True]
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.is_repo()
        self.assertTrue(mock_exists.call_count, 5)
        self.assertFalse(status)

        mock_exists.side_effect = [True, True, True, True,
                                   True]
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.is_repo()
        self.assertTrue(mock_exists.call_count, 5)
        self.assertTrue(status)

    def test_05_is_container_id(self):
        """Test05 LocalRepository().is_container_id()."""
        contid = ""
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.is_container_id(contid)
        self.assertFalse(status)

        contid = "d2578feb-acfc-37e0-8561-47335f85e46a"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.is_container_id(contid)
        self.assertTrue(status)

        contid = "d"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.is_container_id(contid)
        self.assertFalse(status)

    @patch.object(LocalRepository, '_protect')
    def test_06_protect_container(self, mock_prot):
        """Test06 LocalRepository().protect_container()."""
        contid = "d2578feb-acfc-37e0-8561-47335f85e46a"
        mock_prot.return_value = True
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.protect_container(contid)
        self.assertTrue(status)
        self.assertTrue(mock_prot.called)

    @patch.object(LocalRepository, '_unprotect')
    def test_07_unprotect_container(self, mock_unprot):
        """Test07 LocalRepository().unprotect_container()."""
        contid = "d2578feb-acfc-37e0-8561-47335f85e46a"
        mock_unprot.return_value = True
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.unprotect_container(contid)
        self.assertTrue(status)
        self.assertTrue(mock_unprot.called)

    @patch.object(LocalRepository, '_isprotected')
    def test_08_isprotected_container(self, mock_isprot):
        """Test08 LocalRepository().isprotected_container()."""
        contid = "d2578feb-acfc-37e0-8561-47335f85e46a"
        mock_isprot.return_value = True
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.isprotected_container(contid)
        self.assertTrue(status)
        self.assertTrue(mock_isprot.called)

    def test_09__protect(self):
        """Test09 LocalRepository()._protect()."""
        cdir = "/home/u1/.udocker/contid"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        with patch(BOPEN, mock_open()):
            status = lrepo._protect(cdir)
            self.assertTrue(status)

    @patch('udocker.container.localrepo.FileUtil.remove')
    def test_10__unprotect(self, mock_furm):
        """Test10 LocalRepository()._unprotect()."""
        cdir = "/home/u1/.udocker/contid"
        mock_furm.return_value = True
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo._unprotect(cdir)
        self.assertTrue(status)
        self.assertTrue(mock_furm.called)

    @patch('udocker.container.localrepo.os.path.exists')
    def test_11__isprotected(self, mock_exists):
        """Test11 LocalRepository()._isprotected()."""
        cdir = "/home/u1/.udocker/contid"
        mock_exists.return_value = True
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo._isprotected(cdir)
        self.assertTrue(status)
        self.assertTrue(mock_exists.called)

    @patch.object(LocalRepository, 'cd_container')
    @patch('udocker.container.localrepo.os.access')
    @patch('udocker.container.localrepo.os.path.isdir')
    @patch('udocker.container.localrepo.os.path.exists')
    def test_12_iswriteable_container(self, mock_exists,
                                      mock_isdir, mock_access,
                                      mock_cdcont):
        """Test12 LocalRepository().iswriteable_container()."""
        container_id = "d2578feb-acfc-37e0-8561-47335f85e46a"
        mock_exists.return_value = False
        mock_cdcont.return_value = "/home/u1/.udocker/containerid"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.iswriteable_container(container_id)
        self.assertEqual(status, 2)
        self.assertTrue(mock_exists.called)

        mock_exists.return_value = True
        mock_isdir.return_value = False
        mock_cdcont.return_value = "/home/u1/.udocker/containerid"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.iswriteable_container(container_id)
        self.assertEqual(status, 3)
        self.assertTrue(mock_isdir.called)

        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_access.return_value = True
        mock_cdcont.return_value = "/home/u1/.udocker/containerid"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.iswriteable_container(container_id)
        self.assertEqual(status, 1)
        self.assertTrue(mock_access.called)

        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_access.return_value = False
        mock_cdcont.return_value = "/home/u1/.udocker/containerid"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.iswriteable_container(container_id)
        self.assertEqual(status, 0)

    @patch.object(LocalRepository, 'cd_container')
    @patch('udocker.container.localrepo.Uprocess.get_output')
    def test_13_get_size(self, mock_getout, mock_cdcont):
        """Test13 LocalRepository().get_size()."""
        container_id = "d2578feb-acfc-37e0-8561-47335f85e46a"
        mock_getout.return_value = "1234 dd"
        mock_cdcont.return_value = "/home/u1/.udocker/containerid"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.get_size(container_id)
        self.assertEqual(status, 1234)
        self.assertTrue(mock_getout.called)

        container_id = "d2578feb-acfc-37e0-8561-47335f85e46a"
        mock_getout.return_value = ""
        mock_cdcont.return_value = "/home/u1/.udocker/containerid"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.get_size(container_id)
        self.assertEqual(status, -1)

    @patch.object(LocalRepository, 'get_container_name')
    @patch('udocker.container.localrepo.os.path.islink')
    @patch('udocker.container.localrepo.os.path.isdir')
    @patch('udocker.container.localrepo.os.listdir')
    def test_14_get_containers_list(self, mock_listdir, mock_isdir,
                                    mock_islink, mock_getname):
        """Test14 LocalRepository().get_containers_list() - 01."""
        mock_isdir.return_value = False
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.get_containers_list()
        self.assertEqual(status, list())

        mock_isdir.return_value = False
        mock_listdir.return_value = ["LINK"]
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.get_containers_list()
        self.assertEqual(status, list())

        # mock_isdir.return_value = True
        # mock_listdir.return_value = ["LINK"]
        # with patch(BOPEN, mock_open(read_data='REPONAME')):
        #     lrepo = LocalRepository(UDOCKER_TOPDIR)
        #     containers_list = lrepo.get_containers_list()
        #     self.assertEqual(os.path.basename(containers_list[0]), "LINK")

        # mock_isdir.return_value = True
        # mock_listdir.return_value = ["LINK"]
        # mock_islink.return_value = False
        # mock_getname.return_value = ["NAME1", "NAME2"]
        # with patch(BOPEN, mock_open(read_data='REPONAME')):
        #     lrepo = LocalRepository(UDOCKER_TOPDIR)
        #     containers_list = lrepo.get_containers_list(False)
        #     self.assertEqual(os.path.basename(containers_list[0][1]),
        #                      "REPONAME")

    @patch.object(LocalRepository, 'cd_container')
    @patch.object(LocalRepository, '_name_is_valid')
    @patch('udocker.container.localrepo.FileUtil.remove')
    @patch('udocker.container.localrepo.os.path.exists')
    def test_15_del_container_name(self, mock_exists, mock_remove,
                                   mock_namevalid, mock_cdcont):
        """Test15 LocalRepository().del_container_name()."""
        cont_id = "d2578feb-acfc-37e0-8561-47335f85e46a"
        mock_cdcont.return_value = ""
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.del_container_name(cont_id)
        self.assertFalse(status)

        # mock_cdcont.return_value = "/home/u1/.udocker/containerid"
        # mock_namevalid.return_value = False
        # mock_exists.return_value = True
        # mock_remove.return_value = True
        # lrepo = LocalRepository(UDOCKER_TOPDIR)
        # status = lrepo.del_container_name("NAMEALIAS")
        # self.assertFalse(status)

    #     mock_namevalid.return_value = True
    #     mock_exists.return_value = False
    #     mock_remove.return_value = True
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo.del_container_name("NAMEALIAS")
    #     self.assertFalse(status)

    #     mock_namevalid.return_value = True
    #     mock_exists.return_value = True
    #     mock_remove.return_value = True
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo.del_container_name("NAMEALIAS")
    #     self.assertTrue(status)

    #     mock_namevalid.return_value = True
    #     mock_exists.return_value = True
    #     mock_remove.return_value = False
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo.del_container_name("NAMEALIAS")
    #     self.assertFalse(status)






    @patch('udocker.container.localrepo.os.readlink')
    @patch('udocker.container.localrepo.os.path.islink')
    @patch('udocker.container.localrepo.os.listdir')
    @patch('udocker.container.localrepo.os.path.isdir')
    def test_06_get_container_name(self, mock_isdir, mock_listdir,
                                   mock_islink, mock_readlink):
        """Test LocalRepository().get_container_name()."""
        mock_isdir.return_value = True
        mock_listdir.return_value = ['LINK']
        mock_islink.return_value = True
        mock_readlink.return_value = "/a/b/IMAGE:TAG"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        name_list = lrepo.get_container_name("IMAGE:TAG")
        self.assertEqual(name_list, ["LINK"])



    def test_12_protect_imagerepo(self):
        """Test LocalRepository().protect_imagerepo()."""
        with patch(BOPEN, mock_open()) as mopen:
            lrepo = LocalRepository(UDOCKER_TOPDIR)
            lrepo.protect_imagerepo("IMAGE", "TAG")
            self.assertTrue(mopen.called)
            protect = lrepo.reposdir + "/IMAGE/TAG/PROTECT"
            self.assertEqual(mopen.call_args, call(protect, 'w'))

    @patch('udocker.container.localrepo.os.path.exists')
    def test_13_isprotected_imagerepo(self, mock_exists):
        """Test LocalRepository().isprotected_imagerepo()."""
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.isprotected_imagerepo("IMAGE", "TAG")
        self.assertTrue(mock_exists.called)

        lrepo = LocalRepository(UDOCKER_TOPDIR)
        protect = lrepo.reposdir + "/IMAGE/TAG/PROTECT"
        self.assertEqual(mock_exists.call_args, call(protect))

    @patch.object(LocalRepository, '_unprotect')
    def test_14_unprotect_imagerepo(self, mock_unprotect):
        """Test LocalRepository().unprotected_imagerepo()."""
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.unprotect_imagerepo("IMAGE", "TAG")
        self.assertTrue(mock_unprotect.called)



    @patch('udocker.container.localrepo.os.symlink')
    @patch('udocker.container.localrepo.os.path.exists')
    def test_17__symlink(self, mock_exists, mock_symlink):
        """Test LocalRepository()._symlink()."""
        mock_exists.return_value = True
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo._symlink("EXISTINGFILE", "LINKFILE")
        self.assertFalse(status)

        mock_exists.return_value = False
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo._symlink("EXISTINGFILE", "LINKFILE")
        self.assertTrue(status)

    @patch('udocker.container.localrepo.os.path.exists')
    @patch.object(LocalRepository, '_symlink')
    @patch.object(LocalRepository, 'cd_container')
    def test_18_set_container_name(self, mock_cd, mock_slink, mock_exists):
        """Test LocalRepository().set_container_name()."""
        container_id = "d2578feb-acfc-37e0-8561-47335f85e46a"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.set_container_name(container_id, "WRONG[/")
        self.assertFalse(status)

        mock_cd.return_value = "CONTAINERDIR"
        mock_exists.return_value = True
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.set_container_name(container_id, "RIGHT")
        self.assertFalse(status)

        mock_cd.return_value = "CONTAINERDIR"
        mock_exists.return_value = False
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.set_container_name(container_id, "RIGHT")
        self.assertTrue(status)

    # @patch('udocker.container.localrepo.os.readlink')
    # @patch('udocker.container.localrepo.os.path.isdir')
    # @patch('udocker.container.localrepo.os.path.islink')
    # def test_19_get_container_id(self, mock_islink,
    #                              mock_isdir, mock_readlink):
    #     """Test LocalRepository().get_container_id()."""
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo.get_container_id(None)
    #     self.assertEqual(status, "")

    #     mock_islink.return_value = True
    #     mock_readlink.return_value = "BASENAME"
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo.get_container_id("ALIASNAM")
    #     self.assertEqual(status, "BASENAME")

    #     mock_islink.return_value = False
    #     mock_isdir.return_value = False
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo.get_container_id("ALIASNAM")
    #     self.assertEqual(status, "")

    #     mock_islink.return_value = False
    #     mock_isdir.return_value = True
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo.get_container_id("ALIASNAM")
    #     self.assertEqual(status, "ALIASNAM")

    @patch('udocker.container.localrepo.os.makedirs')
    @patch('udocker.container.localrepo.os.path.exists')
    def test_20_setup_container(self, mock_exists, mock_makedirs):
        """Test LocalRepository().setup_container()."""
        mock_exists.return_value = True
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.setup_container("REPO", "TAG", "ID")
        self.assertEqual(status, "")

        mock_exists.return_value = False
        with patch(BOPEN, mock_open()):
            lrepo = LocalRepository(UDOCKER_TOPDIR)
            status = lrepo.setup_container("REPO", "TAG", "ID")
            self.assertEqual(status, lrepo.containersdir + "/ID")
            self.assertEqual(lrepo.cur_containerdir,
                             lrepo.containersdir + "/ID")

    # @patch('udocker.container.localrepo.FileUtil.remove')
    # @patch('udocker.container.localrepo.os.readlink')
    # @patch('udocker.container.localrepo.os.path.islink')
    # @patch('udocker.container.localrepo.os.listdir')
    # @patch.object(LocalRepository, '_inrepository')
    # def test_21__remove_layers(self, mock_in, mock_listdir, mock_islink,
    #                            mock_readlink, mock_remove):
    #     """Test LocalRepository()._remove_layers()."""
    #     mock_listdir.return_value = []
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo._remove_layers("TAG_DIR", False)
    #     self.assertTrue(status)

    #     mock_listdir.return_value = ["FILE1,", "FILE2"]
    #     mock_islink.return_value = False
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo._remove_layers("TAG_DIR", False)
    #     self.assertTrue(status)

    #     mock_islink.return_value = True
    #     mock_readlink.return_value = "REALFILE"
    #     mock_remove.return_value = False
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo._remove_layers("TAG_DIR", False)
    #     self.assertFalse(status)

    #     mock_remove.return_value = True
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo._remove_layers("TAG_DIR", False)
    #     self.assertTrue(status)

    #     mock_remove.return_value = True
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo._remove_layers("TAG_DIR", True)
    #     self.assertTrue(status)

    #     mock_remove.return_value = False
    #     mock_in.return_value = False
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo._remove_layers("TAG_DIR", True)
    #     self.assertTrue(status)

    #     mock_remove.return_value = False
    #     mock_in.return_value = False
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo._remove_layers("TAG_DIR", False)
    #     self.assertFalse(status)

    #     mock_remove.return_value = False
    #     mock_in.return_value = True
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo._remove_layers("TAG_DIR", True)
    #     self.assertTrue(status)

    @patch('udocker.container.localrepo.FileUtil.remove')
    @patch.object(LocalRepository, 'cd_imagerepo')
    @patch.object(LocalRepository, '_remove_layers')
    def test_22_del_imagerepo(self, mock_rmlayers, mock_cd, mock_remove):
        """Test LocalRepository()._del_imagerepo()."""
        mock_cd.return_value = False
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.del_imagerepo("IMAGE", "TAG", False)
        self.assertFalse(status)

        mock_cd.return_value = True
        mock_remove.return_value = True
        mock_rmlayers.return_value = True
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.cur_repodir = "XXXX"
        lrepo.cur_tagdir = "XXXX"
        status = lrepo.del_imagerepo("IMAGE", "TAG", False)
        self.assertEqual(lrepo.cur_repodir, "")
        self.assertEqual(lrepo.cur_tagdir, "")
        self.assertTrue(status)

    # def _sideffect_test_23(self, arg):
    #     """Side effect for isdir on test 23 _get_tags()."""
    #     if self.iter < 3:
    #         self.iter += 1
    #         return False
    #     else:
    #         return True

    # @patch('udocker.container.localrepo.os.path.isdir')
    # @patch('udocker.container.localrepo.os.listdir')
    # @patch.object(LocalRepository, '_is_tag')
    # def test_23__get_tags(self, mock_is, mock_listdir, mock_isdir):
    #     """Test LocalRepository()._get_tags()."""
    #     mock_isdir.return_value = False
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo._get_tags("CONTAINERS_DIR")
    #     self.assertEqual(status, [])

    #     mock_isdir.return_value = True
    #     mock_listdir.return_value = []
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo._get_tags("CONTAINERS_DIR")
    #     self.assertEqual(status, [])

    #     mock_isdir.return_value = True
    #     mock_listdir.return_value = ["FILE1", "FILE2"]
    #     mock_is.return_value = False
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo._get_tags("CONTAINERS_DIR")
    #     self.assertEqual(status, [])

    #     mock_isdir.return_value = True
    #     mock_listdir.return_value = ["FILE1", "FILE2"]
    #     mock_is.return_value = True
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo._get_tags("CONTAINERS_DIR")
    #     expected_status = [('CONTAINERS_DIR', 'FILE1'),
    #                        ('CONTAINERS_DIR', 'FILE2')]
    #     self.assertEqual(status, expected_status)

    #     mock_isdir.return_value = True
    #     mock_listdir.return_value = ["FILE1", "FILE2"]
    #     mock_is.return_value = False
    #     self.iter = 0
    #     mock_isdir.side_effect = self._sideffect_test_23
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo._get_tags("CONTAINERS_DIR")
    #     expected_status = [('CONTAINERS_DIR', 'FILE1'),
    #                        ('CONTAINERS_DIR', 'FILE2')]
    #     self.assertEqual(self.iter, 2)
    #     self.assertEqual(status, [])

    @patch('udocker.container.localrepo.FileUtil.remove')
    @patch('udocker.container.localrepo.os.path.islink')
    @patch('udocker.container.localrepo.os.path.exists')
    @patch('udocker.container.localrepo.FileUtil')
    def test_24_add_image_layer(self, mock_futil, mock_exists,
                                mock_islink, mock_remove):
        """Test LocalRepository().add_image_layer()."""
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.cur_repodir = ""
        lrepo.cur_tagdir = ""
        status = lrepo.add_image_layer("FILE")
        self.assertFalse(status)

        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.cur_repodir = "IMAGE"
        lrepo.cur_tagdir = "TAG"
        status = lrepo.add_image_layer("FILE")
        self.assertTrue(status)

        mock_exists.return_value = False
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.add_image_layer("FILE")
        self.assertFalse(status)

        mock_exists.return_value = True
        mock_islink.return_value = True
        mock_remove.return_value = True
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.add_image_layer("FILE")
        self.assertTrue(mock_futil.called)
        # self.assertTrue(status)

        mock_exists.return_value = True
        mock_islink.return_value = False
        mock_futil.reset_mock()
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.add_image_layer("FILE")
        # self.assertFalse(mock_futil.called)
        # self.assertTrue(status)

    @patch('udocker.container.localrepo.os.makedirs')
    @patch('udocker.container.localrepo.os.path.exists')
    def test_25_setup_imagerepo(self, mock_exists, mock_makedirs):
        """Test LocalRepository().setup_imagerepo()."""
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.setup_imagerepo("")
        self.assertFalse(status)

        mock_exists.return_value = True
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.setup_imagerepo("IMAGE")
        expected_directory = lrepo.reposdir + "/IMAGE"
        self.assertEqual(lrepo.cur_repodir, expected_directory)
        self.assertFalse(status)

        mock_exists.return_value = False
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.setup_imagerepo("IMAGE")
        expected_directory = lrepo.reposdir + "/IMAGE"
        self.assertTrue(mock_makedirs.called)
        self.assertEqual(lrepo.cur_repodir, expected_directory)
        self.assertTrue(status)

    @patch('udocker.container.localrepo.os.makedirs')
    @patch('udocker.container.localrepo.os.path.exists')
    def test_26_setup_tag(self, mock_exists, mock_makedirs):
        """Test LocalRepository().setup_tag()."""
        mock_exists.return_value = False
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.cur_repodir = lrepo.reposdir + "/IMAGE"
        with patch(BOPEN, mock_open()) as mopen:
            status = lrepo.setup_tag("NEWTAG")
            self.assertTrue(mock_makedirs.called)
            expected_directory = lrepo.reposdir + "/IMAGE/NEWTAG"
            self.assertEqual(lrepo.cur_tagdir, expected_directory)
            self.assertTrue(mopen.called)
            self.assertTrue(status)

    @patch('udocker.container.localrepo.os.listdir')
    @patch('udocker.container.localrepo.os.makedirs')
    @patch('udocker.container.localrepo.os.path.exists')
    def test_27_set_version(self, mock_exists, mock_makedirs, mock_listdir):
        """Test LocalRepository().set_version()."""
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.set_version("v1")
        self.assertFalse(mock_exists.called)
        self.assertFalse(status)

        mock_exists.return_value = False
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.cur_repodir = lrepo.reposdir + "/IMAGE"
        lrepo.cur_tagdir = lrepo.cur_repodir + "/TAG"
        status = lrepo.set_version("v1")
        self.assertFalse(mock_listdir.called)
        self.assertFalse(status)

        mock_exists.return_value = True
        with patch(BOPEN, mock_open()) as mopen:
            lrepo = LocalRepository(UDOCKER_TOPDIR)
            status = lrepo.set_version("v1")
            # self.assertTrue(mock_listdir.called)
            # self.assertTrue(mopen.called)
            # self.assertTrue(status)

    # @patch.object(LocalRepository, 'save_json')
    # @patch.object(LocalRepository, 'load_json')
    # @patch('udocker.container.localrepo.os.path.exists')
    # def test_28_get_image_attributes(self, mock_exists, mock_loadjson,
    #                                  mock_savejson):
    #     """Test LocalRepository().get_image_attributes()."""
    #     mock_exists.return_value = True
    #     mock_loadjson.return_value = None
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo.get_image_attributes()
    #     self.assertEqual((None, None), status)

    #     mock_exists.side_effect = [True, False]
    #     mock_loadjson.side_effect = [("foolayername",), ]
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo.get_image_attributes()
    #     self.assertEqual((None, None), status)

    #     mock_exists.side_effect = [True, True, False]
    #     mock_loadjson.side_effect = [("foolayername",), "foojson"]
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo.get_image_attributes()
    #     self.assertEqual((None, None), status)

    #     mock_exists.side_effect = [True, True, True]
    #     mock_loadjson.side_effect = [("foolayername",), "foojson"]
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo.get_image_attributes()
    #     self.assertEqual(('foojson', ['/foolayername.layer']), status)

    #     mock_exists.side_effect = [False, True]
    #     mock_loadjson.side_effect = [None, ]
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo.get_image_attributes()
    #     self.assertEqual((None, None), status)

    #     mock_exists.side_effect = [False, True, False]
    #     manifest = {
    #         "fsLayers": ({"blobSum": "foolayername"},),
    #         "history": ({"v1Compatibility": '["foojsonstring"]'},)
    #     }
    #     mock_loadjson.side_effect = [manifest, ]
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo.get_image_attributes()
    #     self.assertEqual((None, None), status)

    #     mock_exists.side_effect = [False, True, True]
    #     mock_loadjson.side_effect = [manifest, ]
    #     lrepo = LocalRepository(UDOCKER_TOPDIR)
    #     status = lrepo.get_image_attributes()
    #     self.assertEqual(([u'foojsonstring'], ['/foolayername']), status)

    @patch('udocker.container.localrepo.json.dump')
    @patch('udocker.container.localrepo.os.path.exists')
    def test_29_save_json(self, mock_exists, mock_jsondump):
        """Test LocalRepository().save_json()."""
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.save_json("filename", "data")
        self.assertFalse(mock_exists.called)
        self.assertFalse(status)

        mock_exists.return_value = False
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.cur_repodir = lrepo.reposdir + "/IMAGE"
        lrepo.cur_tagdir = lrepo.cur_repodir + "/TAG"
        status = lrepo.save_json("filename", "data")
        self.assertTrue(mock_exists.called)
        self.assertFalse(status)

        mock_exists.reset_mock()
        with patch(BOPEN, mock_open()) as mopen:
            lrepo = LocalRepository(UDOCKER_TOPDIR)
            status = lrepo.save_json("/filename", "data")
            self.assertTrue(mopen.called)
            self.assertTrue(status)

        mock_exists.reset_mock()
        with patch(BOPEN, mock_open()) as mopen:
            mopen.side_effect = IOError('foo')
            lrepo = LocalRepository(UDOCKER_TOPDIR)
            status = lrepo.save_json("/filename", "data")
            self.assertTrue(mopen.called)
            self.assertFalse(status)

    @patch('udocker.container.localrepo.json.load')
    @patch('udocker.container.localrepo.os.path.exists')
    def test_30_load_json(self, mock_exists, mock_jsonload):
        """Test LocalRepository().load_json()."""
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.load_json("filename")
        self.assertFalse(mock_exists.called)
        self.assertFalse(status)

        mock_exists.return_value = False
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.cur_repodir = lrepo.reposdir + "/IMAGE"
        lrepo.cur_tagdir = lrepo.cur_repodir + "/TAG"
        status = lrepo.load_json("filename")
        self.assertTrue(mock_exists.called)
        self.assertFalse(status)

        mock_exists.reset_mock()
        with patch(BOPEN, mock_open()) as mopen:
            lrepo = LocalRepository(UDOCKER_TOPDIR)
            status = lrepo.load_json("/filename")
            self.assertTrue(mopen.called)
            self.assertTrue(status)

        mock_exists.reset_mock()
        with patch(BOPEN, mock_open()) as mopen:
            mopen.side_effect = IOError('foo')
            lrepo = LocalRepository(UDOCKER_TOPDIR)
            status = lrepo.load_json("/filename")
            self.assertTrue(mopen.called)
            self.assertFalse(status)

    @patch('udocker.container.localrepo.FileUtil')
    def test_31__protect(self, mock_futil):
        """Test LocalRepository()._protect().

        Set the protection mark in a container or image tag
        """
        mock_futil.return_value.isdir.return_value = True
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo._protect
        self.assertTrue(status)

    @patch('udocker.container.localrepo.FileUtil.remove')
    def test_32__unprotect(self, mock_rm):
        """Test LocalRepository()._unprotect().
        Remove protection mark from container or image tag.
        """
        mock_rm.return_value = True
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo._unprotect("dir")
        self.assertTrue(mock_rm.called)
        self.assertTrue(status)

    @patch('udocker.container.localrepo.FileUtil')
    @patch('udocker.container.localrepo.os.path.exists')
    def test_33__isprotected(self, mock_exists, mock_futil):
        """Test LocalRepository()._isprotected().
        See if container or image tag are protected.
        """
        mock_futil.return_value.isdir.return_value = True
        mock_exists.return_value = True
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo._isprotected("dir")
        self.assertTrue(status)

    @patch.object(LocalRepository, 'cd_container')
    @patch.object(LocalRepository, 'get_containers_list')
    def test_34_del_container(self, mock_cdcont, mock_getcl):
        """Test LocalRepository().del_container()."""
        container_id = "d2578feb-acfc-37e0-8561-47335f85e46a"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.del_container(container_id)
        self.assertTrue(mock_cdcont.called)
        self.assertFalse(status)

        mock_cdcont.return_value = ""
        mock_getcl.return_value = "tmp"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.del_container(container_id)
        self.assertFalse(status)

        mock_cdcont.return_value = "/tmp"
        mock_getcl.return_value = "/tmp"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo.del_container(container_id)
        # self.assertTrue(status)

    def test_35__relpath(self):
        """Test LocalRepository()._relpath()."""
        pass

    def test_36__name_is_valid(self):
        """Test LocalRepository()._name_is_valid().
        Check name alias validity.
        """
        name = "lzskjghdlak"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo._name_is_valid(name)
        self.assertTrue(status)

        name = "lzskjghd/lak"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo._name_is_valid(name)
        self.assertFalse(status)

        name = ".lzsklak"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo._name_is_valid(name)
        self.assertFalse(status)

        name = "]lzsklak"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo._name_is_valid(name)
        self.assertFalse(status)

        name = "lzs[klak"
        status = lrepo._name_is_valid(name)
        self.assertFalse(status)

        name = "lzs klak"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo._name_is_valid(name)
        self.assertFalse(status)

        name = "x" * 2049
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo._name_is_valid(name)
        self.assertFalse(status)

    @patch('udocker.container.localrepo.FileUtil')
    @patch('udocker.container.localrepo.os.path.isfile')
    def test_37__is_tag(self, mock_isfile, mock_futil):
        """Test LocalRepository()._is_tag().
        Does this directory contain an image tag ?
        An image TAG indicates that this repo directory
        contains references to layers and metadata from
        which we can extract a container.
        """
        mock_isfile.return_value = True
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo._is_tag("tagdir")
        self.assertTrue(status)

        mock_isfile.return_value = False
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo._is_tag("tagdir")
        self.assertFalse(status)

    @patch('udocker.container.localrepo.os.path.exists')
    def test_38_cd_imagerepo(self, mock_exists):
        """Test LocalRepository().cd_imagerepo()."""
        Config().conf['reposdir'] = "/tmp"
        mock_exists.return_value = True
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.setup("YYYY")
        out = lrepo.cd_imagerepo("IMAGE", "TAG")
        # self.assertNotEqual(out, "")

    @patch('udocker.container.localrepo.FileUtil')
    @patch('udocker.container.localrepo.os.path.islink')
    @patch('udocker.container.localrepo.os.path.isdir')
    @patch('udocker.container.localrepo.os.listdir')
    def test_39__find(self, mock_listdir, mock_isdir, mock_islink, mock_futil):
        """Test LocalRepository()._find().
        is a specific layer filename referenced by another image TAG
        """
        mock_futil.return_value.isdir.return_value = True
        mock_listdir.return_value = ["file"]
        mock_islink.return_value = True
        filename = "file"
        folder = "/tmp"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        out = lrepo._find(filename, folder)
        self.assertEqual(out, ["/tmp/file"])

        mock_islink.return_value = False
        mock_isdir.return_value = False
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        out = lrepo._find(filename, folder)
        self.assertEqual(out, [])

    @patch('udocker.container.localrepo.FileUtil')
    @patch('udocker.container.localrepo.os.path.islink')
    @patch('udocker.container.localrepo.os.path.isdir')
    @patch('udocker.container.localrepo.os.listdir')
    def test_40__inrepository(self, mock_listdir,
                              mock_isdir, mock_islink, mock_futil):
        """Test LocalRepository()._inrepository().
        Check if a given file is in the repository.
        """
        mock_futil.return_value.isdir.return_value = True
        mock_listdir.return_value = ["file"]
        mock_islink.return_value = True
        filename = "file"
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.reposdir = "/tmp"
        out = lrepo._inrepository(filename)
        self.assertEqual(out, ["/tmp/file"])

        mock_islink.return_value = False
        mock_isdir.return_value = False
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        out = lrepo._inrepository(filename)
        self.assertEqual(out, [])

    @patch('udocker.container.localrepo.FileUtil.remove')
    @patch('udocker.container.localrepo.os.path.islink')
    @patch('udocker.container.localrepo.os.readlink')
    @patch('udocker.container.localrepo.os.listdir')
    @patch('udocker.container.localrepo.os.path.realpath')
    def test_41__remove_layers(self, mock_realpath, mock_listdir,
                               mock_readlink, mock_islink, mock_remove):
        """Test LocalRepository()._remove_layers().
        Remove link to image layer and corresponding layer
        if not being used by other images.
        """
        mock_realpath.return_value = "/tmp"
        mock_listdir.return_value = "file"
        mock_islink.return_value = True
        mock_readlink.return_value = "file"
        tag_dir = "TAGDIR"
        mock_remove.return_value = False
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.reposdir = "/tmp"
        status = lrepo._remove_layers(tag_dir, True)
        self.assertTrue(status)

        mock_remove.return_value = False
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        status = lrepo._remove_layers(tag_dir, False)
        # (FIXME lalves): This is not OK, it should be False. Review this test.
        self.assertFalse(status)

    @patch.object(LocalRepository, '_get_tags')
    def test_42_get_imagerepos(self, mock_gtags):
        """Test LocalRepository().get_imagerepos()."""
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.get_imagerepos()
        self.assertTrue(mock_gtags.called)

    @patch.object(LocalRepository, 'cd_container')
    def test_43_get_layers(self, mock_cd):
        """Test LocalRepository().get_layers()."""
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.get_layers("IMAGE", "TAG")
        # self.assertTrue(mock_cd.called)

    @patch('udocker.container.localrepo.os.path.isdir')
    @patch.object(LocalRepository, 'load_json')
    @patch('udocker.container.localrepo.os.listdir')
    def test_44__load_structure(self, mock_listdir, mock_json, mock_isdir):
        """Test LocalRepository()._load_structure().
        Scan the repository structure of a given image tag.
        """
        mock_isdir.return_value = False
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        structure = lrepo._load_structure("IMAGETAGDIR")
        # self.assertTrue(structure["layers"])

        mock_isdir.return_value = True
        mock_listdir.return_value = ["ancestry"]
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.return_value = "JSON"
        structure = lrepo._load_structure("IMAGETAGDIR")
        # WIP
        # self.assertTrue("JSON" in structure["ancestry"])

    def test_45__find_top_layer_id(self):
        """Test LocalRepository()._find_top_layer_id"""
        pass

    def test_46__sorted_layers(self):
        """Test LocalRepository()._sorted_layers"""
        pass

    def test_47__verify_layer_file(self):
        """Test LocalRepository()._verify_layer_file"""
        pass

    @patch('udocker.container.localrepo.Msg')
    @patch.object(LocalRepository, '_load_structure')
    def test_48_verify_image(self, mock_lstruct, mock_msg):
        """Test LocalRepository().verify_image()."""
        mock_msg.level = 0
        lrepo = LocalRepository(UDOCKER_TOPDIR)
        lrepo.verify_image()
        self.assertTrue(mock_lstruct.called)


if __name__ == '__main__':
    main()
