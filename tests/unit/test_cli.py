#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
udocker unit tests: UdockerCLI
"""

import sys
sys.path.append('.')
sys.path.append('../../')

from udocker.config import Config
from udocker.cmdparser import CmdParser
from udocker.cli import UdockerCLI
from unittest import TestCase, main
try:
    from unittest.mock import Mock, patch, MagicMock, mock_open
except ImportError:
    from mock import Mock, patch, MagicMock, mock_open

if sys.version_info[0] >= 3:
    BUILTIN = "builtins"
else:
    BUILTIN = "__builtin__"

BOPEN = BUILTIN + '.open'


class UdockerCLITestCase(TestCase):
    """Test UdockerTestCase() command line interface."""

    def setUp(self):
        Config().getconf()
        Config().conf['hostauth_list'] = ("/etc/passwd", "/etc/group")
        Config().conf['cmd'] = "/bin/bash"
        Config().conf['cpu_affinity_exec_tools'] = (["numactl", "-C", "%s", "--", ],
                                                ["taskset", "-c", "%s", ])
        Config().conf['valid_host_env'] = "HOME"
        Config().conf['username'] = "user"
        Config().conf['userhome'] = "/"
        Config().conf['oskernel'] = "4.8.13"
        Config().conf['location'] = ""
        Config().conf['keystore'] = "KEYSTORE"

        str_local = 'udocker.container.localrepo.LocalRepository'
        self.lrepo = patch(str_local)
        self.local = self.lrepo.start()
        self.mock_lrepo = Mock()
        self.local.return_value = self.mock_lrepo

    def tearDown(self):
        self.lrepo.stop()

    @patch('udocker.cli.LocalFileAPI')
    @patch('udocker.cli.KeyStore')
    @patch('udocker.cli.DockerIoAPI')
    def test_01_init(self, mock_dioapi, mock_ks, mock_lfapi):
        """Test01 UdockerCLI() constructor."""
        # Test Config().conf['keystore'] starts with /
        Config().conf['keystore'] = "/xxx"
        udoc = UdockerCLI(self.local)
        self.assertTrue(mock_dioapi.called)
        self.assertTrue(mock_lfapi.called)
        self.assertTrue(mock_ks.called_with(Config().conf['keystore']))

        # Test Config().conf['keystore'] does not starts with /
        Config().conf['keystore'] = "xx"
        udoc = UdockerCLI(self.local)
        self.assertTrue(mock_ks.called_with(Config().conf['keystore']))

    @patch('udocker.cli.FileUtil.isdir')
    def test_02__cdrepo(self, mock_isdir):
        """Test02 UdockerCLI()._cdrepo()."""
        argv = ["udocker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = UdockerCLI(self.local)
        status = udoc._cdrepo(cmdp)
        self.assertFalse(status)
        self.assertFalse(mock_isdir.called)

        argv = ["udocker"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_isdir.return_value = False
        udoc = UdockerCLI(self.local)
        status = udoc._cdrepo(cmdp)
        self.assertFalse(status)
        self.assertTrue(mock_isdir.called)

        argv = ["udocker"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_isdir.return_value = True
        self.local.setup.return_value = None
        udoc = UdockerCLI(self.local)
        status = udoc._cdrepo(cmdp)
        self.assertTrue(status)
        self.assertTrue(self.local.setup.called)

    @patch('udocker.cli.DockerIoAPI.is_repo_name')
    @patch('udocker.cli.Msg')
    def test_03__check_imagespec(self, mock_msg, mock_reponame):
        """Test03 UdockerCLI()._check_imagespec()."""
        mock_msg.level = 0
        mock_reponame.return_value = False
        udoc = UdockerCLI(self.local)
        status = udoc._check_imagespec("")
        self.assertEqual(status, (None, None))

        mock_reponame.return_value = True
        udoc = UdockerCLI(self.local)
        status = udoc._check_imagespec("AAA")
        self.assertEqual(status, ("AAA", "latest"))

        mock_reponame.return_value = True
        udoc = UdockerCLI(self.local)
        status = udoc._check_imagespec("AAA:45")
        self.assertEqual(status, ("AAA", "45"))

    @patch('udocker.cli.DockerIoAPI.is_repo_name')
    @patch('udocker.cli.Msg')
    def test_04__check_imagerepo(self, mock_msg, mock_reponame):
        """Test04 UdockerCLI()._check_imagerepo()."""
        mock_msg.level = 0
        mock_reponame.return_value = False
        udoc = UdockerCLI(self.local)
        status = udoc._check_imagerepo("")
        self.assertEqual(status, None)

        mock_reponame.return_value = True
        udoc = UdockerCLI(self.local)
        status = udoc._check_imagerepo("AAA")
        self.assertEqual(status, "AAA")

    # def test_05__set_repository(self):
    #     """Test05 UdockerCLI()._set_repository()."""

    def test_06__split_imagespec(self):
        """Test06 UdockerCLI()._split_imagespec()."""
        imgrepo = ""
        res = ("", "", "", "")
        udoc = UdockerCLI(self.local)
        status = udoc._split_imagespec(imgrepo)
        self.assertEqual(status, res)

        imgrepo = "dockerhub.io/myimg:1.2"
        res = ("", "dockerhub.io", "myimg", "1.2")
        udoc = UdockerCLI(self.local)
        status = udoc._split_imagespec(imgrepo)
        self.assertEqual(status, res)

        imgrepo = "https://dockerhub.io/myimg:1.2"
        res = ("https:", "dockerhub.io", "myimg", "1.2")
        udoc = UdockerCLI(self.local)
        status = udoc._split_imagespec(imgrepo)
        self.assertEqual(status, res)

    @patch('udocker.cli.os.path.exists')
    @patch('udocker.cli.Msg')
    def test_07_do_mkrepo(self, mock_msg, mock_exists):
        """Test07 UdockerCLI().do_mkrepo()."""
        mock_msg.level = 0

        argv = ["udocker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_exists.return_value = True
        udoc = UdockerCLI(self.local)
        status = udoc.do_mkrepo(cmdp)
        self.assertEqual(status, 1)
        self.assertFalse(mock_exists.called)

        argv = ["udocker", "mkrepo"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_exists.return_value = False
        self.local.setup.return_value = None
        self.local.create_repo.return_value = False
        udoc = UdockerCLI(self.local)
        status = udoc.do_mkrepo(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_exists.called)
        self.assertTrue(self.local.setup.called)
        self.assertTrue(self.local.create_repo.called)

        argv = ["udocker", "mkrepo"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_exists.return_value = False
        self.local.setup.return_value = None
        self.local.create_repo.return_value = True
        udoc = UdockerCLI(self.local)
        status = udoc.do_mkrepo(cmdp)
        self.assertEqual(status, 0)

    # def test_08__search_print_lines(self):
    #     """Test08 UdockerCLI()._search_print_lines()."""

    # @patch('udocker.cli.DockerIoAPI.search_get_page')
    # @patch('udocker.cli.HostInfo.termsize')
    # def test_09__search_repositories(self, mock_termsz, mock_doiasearch):
    #     """Test09 UdockerCLI()._search_repositories()."""
    #     repo_list = {"count": 1, "next": "", "previous": "",
    #                  "results": [
    #                      {
    #                          "repo_name": "lipcomputing/ipyrad",
    #                          "short_description": "Docker to run ipyrad",
    #                          "star_count": 0,
    #                          "pull_count": 188,
    #                          "repo_owner": "",
    #                          "is_automated": True,
    #                          "is_official": False
    #                      }]}
    #     mock_termsz.return_value = (3, "")
    #     mock_doiasearch.return_value = repo_list
    #     udoc = UdockerCLI(self.local)
    #     status = udoc._search_repositories("ipyrad")
    #     self.assertEqual(status, 0)

    @patch('udocker.cli.DockerIoAPI.get_tags')
    def test_10__list_tags(self, mock_gettags):
        """Test10 UdockerCLI()._list_tags()."""
        mock_gettags.return_value = ["t1"]
        udoc = UdockerCLI(self.local)
        status = udoc._list_tags("t1")
        self.assertEqual(status, 0)

        mock_gettags.return_value = None
        udoc = UdockerCLI(self.local)
        status = udoc._list_tags("t1")
        self.assertEqual(status, 1)

    @patch('udocker.cli.KeyStore.get')
    @patch('udocker.cli.DockerIoAPI.set_v2_login_token')
    @patch('udocker.cli.DockerIoAPI.search_init')
    @patch.object(UdockerCLI, '_search_repositories')
    @patch.object(UdockerCLI, '_list_tags')
    @patch.object(UdockerCLI, '_split_imagespec')
    @patch.object(UdockerCLI, '_set_repository')
    def test_11_do_search(self, mock_setrepo, mock_split, mock_listtags,
                          mock_searchrepo, mock_doiasearch, mock_doiasetv2,
                          mock_ksget):
        """Test11 UdockerCLI().do_search()."""
        argv = ["udocker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = UdockerCLI(self.local)
        status = udoc.do_search(cmdp)
        self.assertEqual(status, 1)

        argv = ["udocker", "search", "--list-tags", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_setrepo.return_value = None
        mock_split.return_value = ("d1", "d2", "ipyrad", "d3")
        mock_doiasearch.return_value = None
        mock_ksget.return_value = "v2token1"
        mock_doiasetv2.return_value = None
        mock_listtags.return_value = ["t1", "t2"]
        udoc = UdockerCLI(self.local)
        status = udoc.do_search(cmdp)
        self.assertEqual(status, ["t1", "t2"])
        self.assertTrue(mock_setrepo.called)
        self.assertTrue(mock_doiasearch.called)
        self.assertTrue(mock_ksget.called)
        self.assertTrue(mock_doiasetv2.called)
        self.assertTrue(mock_listtags.called)

        argv = ["udocker", "search", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_setrepo.return_value = None
        mock_split.return_value = ("d1", "d2", "ipyrad", "d3")
        mock_doiasearch.return_value = None
        mock_ksget.return_value = "v2token1"
        mock_doiasetv2.return_value = None
        mock_searchrepo.return_value = 0
        udoc = UdockerCLI(self.local)
        status = udoc.do_search(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_searchrepo.called)

    @patch('udocker.cli.Msg')
    @patch('udocker.cli.LocalFileAPI.load')
    @patch.object(UdockerCLI, '_check_imagerepo')
    def test_12_do_load(self, mock_chkimg, mock_load, mock_msg):
        """Test12 UdockerCLI().do_load()."""
        mock_msg.level = 0
        argv = ["udocker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = UdockerCLI(self.local)
        status = udoc.do_load(cmdp)
        self.assertEqual(status, 1)

        argv = ["udocker", "load", "-i", "ipyrad", "ipyimg"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = False
        udoc = UdockerCLI(self.local)
        status = udoc.do_load(cmdp)
        self.assertEqual(status, 1)
        self.assertFalse(mock_load.called)

        argv = ["udocker", "load", "-i", "ipyrad", "ipyimg"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = True
        mock_load.return_value = False
        udoc = UdockerCLI(self.local)
        status = udoc.do_load(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_load.called)

        argv = ["udocker", "load", "-i", "ipyrad", "ipyimg"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = True
        mock_load.return_value = ['docker-repo1', 'docker-repo2']
        udoc = UdockerCLI(self.local)
        status = udoc.do_load(cmdp)
        self.assertEqual(status, 0)

    @patch('udocker.cli.os.path.exists')
    @patch('udocker.cli.LocalFileAPI.save')
    @patch.object(UdockerCLI, '_check_imagespec')
    def test_13_do_save(self, mock_chkimg, mock_save, mock_exists):
        """Test13 UdockerCLI().do_save()."""
        argv = ["udocker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = UdockerCLI(self.local)
        status = udoc.do_save(cmdp)
        self.assertEqual(status, 1)

        argv = ["udocker", "save", "-o", "ipyrad", "ipyimg:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_exists.return_value = True
        udoc = UdockerCLI(self.local)
        status = udoc.do_save(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_exists.called)
        self.assertFalse(mock_chkimg.called)
        self.assertFalse(mock_save.called)

        argv = ["udocker", "save", "-o", "ipyrad", "ipyimg:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_exists.return_value = False
        mock_chkimg.return_value = ("ipyimg", "latest")
        mock_save.return_value = False
        udoc = UdockerCLI(self.local)
        status = udoc.do_save(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_save.called)

        argv = ["udocker", "save", "-o", "ipyrad", "ipyimg:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_exists.return_value = False
        mock_chkimg.return_value = ("ipyimg", "latest")
        mock_save.return_value = True
        udoc = UdockerCLI(self.local)
        status = udoc.do_save(cmdp)
        self.assertTrue(mock_exists.called)
        self.assertTrue(mock_chkimg.called)
        self.assertTrue(mock_save.called)
        self.assertEqual(status, 0)

    @patch('udocker.cli.LocalFileAPI.import_toimage')
    @patch('udocker.cli.LocalFileAPI.import_tocontainer')
    @patch('udocker.cli.LocalFileAPI.import_clone')
    @patch('udocker.cli.Msg')
    @patch.object(UdockerCLI, '_check_imagespec')
    def test_14_do_import(self, mock_chkimg, mock_msg, mock_impclone,
                          mock_impcont, mock_impimg):
        """Test14 UdockerCLI().do_import()."""
        mock_msg.level = 0
        argv = ["udocker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = UdockerCLI(self.local)
        status = udoc.do_import(cmdp)
        self.assertEqual(status, 1)
        self.assertFalse(mock_chkimg.called)
        self.assertFalse(mock_impclone.called)
        self.assertFalse(mock_impcont.called)
        self.assertFalse(mock_impimg.called)

        argv = ["udocker", "import", "ipyrad.tar", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("", "latest")
        udoc = UdockerCLI(self.local)
        status = udoc.do_import(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_chkimg.called)
        self.assertFalse(mock_impimg.called)

        argv = ["udocker", "import", "ipyrad.tar", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        udoc = UdockerCLI(self.local)
        status = udoc.do_import(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_chkimg.called)
        self.assertTrue(mock_impimg.called)

        argv = ["udocker", "import", "--clone", "ipyrad.tar", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        mock_impclone.return_value = "12345"
        udoc = UdockerCLI(self.local)
        status = udoc.do_import(cmdp)
        self.assertEqual(status, 0)
        self.assertFalse(mock_impcont.called)
        self.assertTrue(mock_impclone.called)

        argv = ["udocker", "import", "--tocontainer",
                "ipyrad.tar", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        mock_impcont.return_value = "12345"
        udoc = UdockerCLI(self.local)
        status = udoc.do_import(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_impcont.called)

    @patch('udocker.cli.ContainerStructure')
    def test_15_do_export(self, mock_cs):
        """Test15 UdockerCLI().do_export()."""
        argv = ["udocker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = UdockerCLI(self.local)
        status = udoc.do_export(cmdp)
        self.assertEqual(status, 1)

        argv = ["udocker", "export", "-o", "ipyrad.tar", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = ""
        udoc = UdockerCLI(self.local)
        status = udoc.do_export(cmdp)
        self.assertEqual(status, 1)

        argv = ["udocker", "export", "-o", "ipyrad.tar", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_cs.return_value.export_tofile.return_value = False
        self.local.get_container_id.return_value = "12345"
        udoc = UdockerCLI(self.local)
        status = udoc.do_export(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_cs.called)
        self.assertTrue(self.local.get_container_id.called)

        argv = ["udocker", "export", "-o", "ipyrad.tar", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_cs.return_value.export_tofile.return_value = True
        self.local.get_container_id.return_value = "12345"
        udoc = UdockerCLI(self.local)
        status = udoc.do_export(cmdp)
        self.assertEqual(status, 0)

        argv = ["udocker", "export",
                "--clone", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_cs.return_value.clone_tofile.return_value = True
        self.local.get_container_id.return_value = "12345"
        udoc = UdockerCLI(self.local)
        status = udoc.do_export(cmdp)
        self.assertEqual(status, 0)

    @patch('udocker.cli.LocalFileAPI.clone_container')
    @patch('udocker.cli.Msg')
    def test_16_do_clone(self, mock_msg, mock_clone):
        """Test16 UdockerCLI().do_clone()."""
        mock_msg.level = 0
        argv = ["udocker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = UdockerCLI(self.local)
        status = udoc.do_clone(cmdp)
        self.assertEqual(status, 1)

        argv = ["udocker", "clone", "ipyradcont"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = ""
        udoc = UdockerCLI(self.local)
        status = udoc.do_clone(cmdp)
        self.assertEqual(status, 1)
        self.assertFalse(mock_clone.called)
        self.assertTrue(self.local.get_container_id.called)

        argv = ["udocker", "clone", "ipyradcont"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = "12345"
        mock_clone.return_value = "54321"
        udoc = UdockerCLI(self.local)
        status = udoc.do_clone(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_clone.called)

    @patch('udocker.cli.KeyStore.put')
    @patch('udocker.cli.DockerIoAPI.get_v2_login_token')
    @patch.object(UdockerCLI, '_set_repository')
    def test_17_do_login(self, mock_setrepo, mock_dioalog, mock_ksput):
        """Test17 UdockerCLI().do_login()."""
        argv = ["udocker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = UdockerCLI(self.local)
        status = udoc.do_login(cmdp)
        self.assertEqual(status, 1)

        argv = ["udocker", "login", "--username", "u1",
                "--password", "xx"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_setrepo.return_value = None
        mock_dioalog.return_value = "zx1"
        mock_ksput.return_value = False
        udoc = UdockerCLI(self.local)
        status = udoc.do_login(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_setrepo.called)
        self.assertTrue(mock_dioalog.called)
        self.assertTrue(mock_ksput.called)

        argv = ["udocker", "login", "--username", "u1",
                "--password", "xx"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_setrepo.return_value = None
        mock_dioalog.return_value = "zx1"
        mock_ksput.return_value = True
        udoc = UdockerCLI(self.local)
        status = udoc.do_login(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_setrepo.called)
        self.assertTrue(mock_dioalog.called)
        self.assertTrue(mock_ksput.called)

    @patch('udocker.cli.Msg')
    @patch('udocker.cli.KeyStore')
    @patch.object(UdockerCLI, '_set_repository')
    def test_18_do_logout(self, mock_setrepo, mock_ks, mock_msg):
        """Test18 UdockerCLI().do_logout()."""
        mock_msg.level = 0
        argv = ["udocker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = UdockerCLI(self.local)
        status = udoc.do_logout(cmdp)
        self.assertEqual(status, 1)

        argv = ["udocker", "logout", "-a"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_setrepo.return_value = None
        mock_ks.return_value.erase.return_value = 0
        udoc = UdockerCLI(self.local)
        status = udoc.do_logout(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(mock_setrepo.called)
        self.assertTrue(mock_ks.return_value.erase.called)

        argv = ["udocker", "logout"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_setrepo.return_value = None
        mock_ks.return_value.delete.return_value = 1
        udoc = UdockerCLI(self.local)
        status = udoc.do_logout(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_setrepo.called)
        self.assertTrue(mock_ks.return_value.delete.called)

    @patch.object(UdockerCLI, '_set_repository')
    @patch.object(UdockerCLI, '_check_imagespec')
    @patch('udocker.cli.DockerIoAPI')
    @patch('udocker.cli.KeyStore.get')
    @patch('udocker.cli.Msg')
    def test_19_do_pull(self, mock_msg, mock_ksget, mock_dioa,
                        mock_chkimg, mock_setrepo):
        """Test19 UdockerCLI().do_pull()."""
        mock_msg.level = 0
        argv = ["udocker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        udoc = UdockerCLI(self.local)
        status = udoc.do_pull(cmdp)
        self.assertEqual(status, 1)

        argv = ["udocker", "pull", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        mock_setrepo.return_value = None
        mock_ksget.return_value = "zx1"
        mock_dioa.return_value.set_v2_login_token.return_value = None
        mock_dioa.return_value.get.return_value = False
        udoc = UdockerCLI(self.local)
        status = udoc.do_pull(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_chkimg.called)
        self.assertTrue(mock_setrepo.called)
        self.assertTrue(mock_ksget.called)
        self.assertTrue(mock_dioa.return_value.set_v2_login_token.called)
        self.assertTrue(mock_dioa.return_value.get.called)

        argv = ["udocker", "pull", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_chkimg.return_value = ("ipyrad", "latest")
        mock_setrepo.return_value = None
        mock_ksget.return_value = "zx1"
        mock_dioa.return_value.set_v2_login_token.return_value = None
        mock_dioa.return_value.get.return_value = True
        udoc = UdockerCLI(self.local)
        status = udoc.do_pull(cmdp)
        self.assertEqual(status, 0)

    @patch.object(UdockerCLI, '_check_imagespec')
    @patch('udocker.cli.ContainerStructure')
    @patch('udocker.cli.DockerIoAPI')
    @patch('udocker.cli.Msg')
    def test_20__create(self, mock_msg, mock_dioapi,
                        mock_cstruct, mock_chkimg):
        """Test20 UdockerCLI()._create()."""
        mock_msg.level = 0
        mock_dioapi.return_value.is_repo_name.return_value = False
        udoc = UdockerCLI(self.local)
        status = udoc._create("IMAGE:TAG")
        self.assertFalse(status)
        self.assertTrue(mock_msg.return_value.err.called)

        mock_dioapi.return_value.is_repo_name.return_value = True
        mock_chkimg.return_value = ("", "TAG")
        mock_cstruct.return_value.create.return_value = True
        udoc = UdockerCLI(self.local)
        status = udoc._create("IMAGE:TAG")
        self.assertFalse(status)

        mock_dioapi.return_value.is_repo_name.return_value = True
        mock_chkimg.return_value = ("IMAGE", "TAG")
        mock_cstruct.return_value.create.return_value = True
        udoc = UdockerCLI(self.local)
        status = udoc._create("IMAGE:TAG")
        self.assertTrue(status)

    @patch.object(UdockerCLI, '_create')
    @patch('udocker.cli.Msg')
    def test_21_do_create(self, mock_msg, mock_create):
        """Test21 UdockerCLI().do_create()."""
        mock_msg.level = 0
        argv = ["udocker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = UdockerCLI(self.local)
        status = udoc.do_create(cmdp)
        self.assertEqual(status, 1)
        self.assertFalse(mock_create.called)

        argv = ["udocker", "create", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_create.return_value = ""
        udoc = UdockerCLI(self.local)
        status = udoc.do_create(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_create.called)

        argv = ["udocker", "create", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_create.return_value = "12345"
        udoc = UdockerCLI(self.local)
        status = udoc.do_create(cmdp)
        self.assertEqual(status, 0)
        self.assertFalse(self.local.set_container_name.called)

        argv = ["udocker", "create", "--name=mycont", "ipyrad:latest"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_create.return_value = "12345"
        self.local.set_container_name.return_value = False
        udoc = UdockerCLI(self.local)
        status = udoc.do_create(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(self.local.set_container_name.called)

    # def test_22__get_run_options(self):
    #    """Test22 UdockerCLI()._get_run_options()"""

    @patch('udocker.cli.ExecutionMode')
    @patch('udocker.cli.Msg')
    @patch.object(UdockerCLI, 'do_pull')
    @patch.object(UdockerCLI, '_create')
    @patch.object(UdockerCLI, '_check_imagespec')
    def test_23_do_run(self, mock_chkimg, mock_create, mock_pull,
                       mock_msg, mock_exec):
        """Test23 UdockerCLI().do_run()."""
        mock_msg.level = 0
        argv = ["udocker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = UdockerCLI(self.local)
        status = udoc.do_run(cmdp)
        self.assertEqual(status, 1)

        argv = ["udocker", "run"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = UdockerCLI(self.local)
        status = udoc.do_run(cmdp)
        self.assertEqual(status, 1)

        argv = ["udocker", "run", "--location=/tmp/udocker", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_exec.return_value.get_engine.return_value = False
        udoc = UdockerCLI(self.local)
        status = udoc.do_run(cmdp)
        self.assertEqual(status, 1)
        self.assertTrue(mock_exec.return_value.get_engine.called)

        exeng_patch = patch("udocker.engine.proot.PRootEngine")
        proot = exeng_patch.start()
        mock_proot = Mock()
        proot.return_value = mock_proot

        argv = ["udocker", "run", "--location=/tmp/udocker", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        mock_exec.return_value.get_engine.return_value = proot
        proot.run.return_value = 0
        udoc = UdockerCLI(self.local)
        status = udoc.do_run(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(proot.run.called)
        self.assertFalse(self.local.isprotected_container.called)

        argv = ["udocker", "run", "ipyrad"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_container_id.return_value = ""
        mock_exec.return_value.get_engine.return_value = proot
        proot.run.return_value = 0
        mock_chkimg.return_value = ("ipyrad", "latest")
        self.local.cd_imagerepo.return_value = True
        mock_create.return_value = "12345"
        udoc = UdockerCLI(self.local)
        status = udoc.do_run(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(self.local.get_container_id.called)
        self.assertTrue(mock_chkimg.called)
        self.assertTrue(self.local.cd_imagerepo.called)
        self.assertTrue(mock_create.called)

        exeng_patch.stop()

    def test_24_do_images(self):
        """Test24 UdockerCLI().do_images()."""
        argv = ["udocker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = UdockerCLI(self.local)
        status = udoc.do_images(cmdp)
        self.assertEqual(status, 1)

        argv = ["udocker", "images", "-l"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_imagerepos.return_value = [("img1", "tag1")]
        self.local.isprotected_imagerepo.return_value = False
        self.local.cd_imagerepo.return_value = "/img1"
        self.local.get_layers.return_value = [("l1", 1024)]
        udoc = UdockerCLI(self.local)
        status = udoc.do_images(cmdp)
        self.assertEqual(status, 0)
        self.assertTrue(self.local.get_imagerepos.called)
        self.assertTrue(self.local.isprotected_imagerepo.called)
        self.assertTrue(self.local.cd_imagerepo.called)
        self.assertTrue(self.local.get_layers.called)

    @patch('udocker.cli.ExecutionMode')
    def test_25_do_ps(self, mock_exec):
        """Test25 UdockerCLI().do_ps()."""
        argv = ["udocker", "-h"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        udoc = UdockerCLI(self.local)
        status = udoc.do_ps(cmdp)
        self.assertEqual(status, 1)

        exeng_patch = patch("udocker.engine.proot.PRootEngine")
        proot = exeng_patch.start()
        mock_proot = Mock()
        proot.return_value = mock_proot
        cdir = "/home/u1/.udocker/containers"
        argv = ["udocker", "ps", "-m", "-s"]
        cmdp = CmdParser()
        cmdp.parse(argv)
        self.local.get_containers_list.return_value = [[cdir, "/", "a"]]
        mock_exec.return_value.get_engine.return_value = proot
        self.local.isprotected_container.return_value = False
        self.local.iswriteable_container.return_value = True
        self.local.get_size.return_value = 1024
        udoc = UdockerCLI(self.local)
        status = udoc.do_ps(cmdp)
        self.assertEqual(status, 0)
        exeng_patch.stop()

    # @patch('udocker.container.localrepo.LocalRepository.del_container', autospec=True)
    # @patch('udocker.container.localrepo.LocalRepository.isprotected_container', autospec=True)
    # @patch('udocker.container.localrepo.LocalRepository.get_container_id', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.get', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.missing_options', autospec=True)
    # @patch('udocker.cli.KeyStore')
    # @patch('udocker.cli.DockerIoAPI')
    # @patch('udocker.cli.Msg')
    # def test_26_do_rm(self, mock_msg, mock_dioapi, mock_ks,
    #                   mock_miss, mock_get, mock_contid, mock_isprotcont, mock_delcont):
    #     """Test26 UdockerCLI().do_rm()."""

    #     mock_msg.level = 0
    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_rm(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_rm(self.cmdp)
    #     self.assertEqual(status, 1)

        # mock_miss.return_value = False
        # mock_get.side_effect = ["X", "12", "" "", "", ]
        # mock_contid.return_value = ""
        # udoc = UdockerCLI(self.local)
        # status = udoc.do_rm(self.cmdp)
        # self.assertEqual(status, 1)

        # mock_miss.return_value = False
        # mock_get.side_effect = ["X", "1", "" "", "", ]
        # mock_contid.return_value = "1"
        # mock_isprotcont.return_value = True
        # udoc = UdockerCLI(self.local)
        # status = udoc.do_rm(self.cmdp)
        # # self.assertEqual(status, 1)

        # mock_miss.return_value = False
        # mock_get.side_effect = ["X", "1", "" "", "", ]
        # mock_contid.return_value = "1"
        # mock_isprotcont.return_value = False
        # mock_delcont.return_value = True
        # udoc = UdockerCLI(self.local)
        # status = udoc.do_rm(self.cmdp)
        # self.assertEqual(status, 0)

    # @patch('udocker.container.localrepo.LocalRepository.del_imagerepo', autospec=True)
    # @patch('udocker.container.localrepo.LocalRepository.isprotected_imagerepo', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.get', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.missing_options', autospec=True)
    # @patch('udocker.cli.UdockerCLI._check_imagespec')
    # @patch('udocker.cli.KeyStore')
    # @patch('udocker.cli.DockerIoAPI')
    # @patch('udocker.cli.Msg')
    # def test_27_do_rmi(self, mock_msg, mock_dioapi, mock_ks,
    #                    mock_chkimg, mock_miss, mock_get, mock_isprotimg, mock_delimg):
    #     """Test27 UdockerCLI().do_rmi()."""

    #     mock_msg.level = 0
    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_rmi(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("", "TAG")
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_rmi(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_isprotimg.return_value = True
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_rmi(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_isprotimg.return_value = False
    #     mock_delimg.return_value = True
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_rmi(self.cmdp)
    #     self.assertEqual(status, 0)

    # @patch('udocker.container.localrepo.LocalRepository.protect_imagerepo', autospec=True)
    # @patch('udocker.container.localrepo.LocalRepository.protect_container', autospec=True)
    # @patch('udocker.container.localrepo.LocalRepository.get_container_id', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.get', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.missing_options', autospec=True)
    # @patch('udocker.cli.UdockerCLI._check_imagespec')
    # @patch('udocker.cli.KeyStore')
    # @patch('udocker.cli.DockerIoAPI')
    # @patch('udocker.cli.Msg')
    # def test_28_do_protect(self, mock_msg, mock_dioapi, mock_ks,
    #                        mock_chkimg, mock_miss, mock_get, mock_contid,
    #                        mock_protcont, mock_protimg):
    #     """Test28 UdockerCLI().do_protect()."""

    #     mock_msg.level = 0
    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_protect(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_contid.return_value = "123"
    #     mock_protcont.return_value = False
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_protect(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_contid.return_value = "123"
    #     mock_protcont.return_value = True
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_protect(self.cmdp)
    #     self.assertEqual(status, 0)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("", "TAG")
    #     mock_contid.return_value = ""
    #     mock_protcont.return_value = True
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_protect(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_contid.return_value = ""
    #     mock_protcont.return_value = True
    #     mock_protimg.return_value = True
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_protect(self.cmdp)
    #     self.assertEqual(status, 0)

    # @patch('udocker.container.localrepo.LocalRepository.unprotect_imagerepo', autospec=True)
    # @patch('udocker.container.localrepo.LocalRepository.unprotect_container', autospec=True)
    # @patch('udocker.container.localrepo.LocalRepository.get_container_id', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.get', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.missing_options', autospec=True)
    # @patch('udocker.cli.UdockerCLI._check_imagespec')
    # @patch('udocker.cli.KeyStore')
    # @patch('udocker.cli.DockerIoAPI')
    # @patch('udocker.cli.Msg')
    # def test_29_do_unprotect(self, mock_msg, mock_dioapi,
    #                          mock_ks, mock_chkimg, mock_miss, mock_get,
    #                          mock_contid, mock_uprotcont, mock_uprotimg):
    #     """Test29 UdockerCLI().do_unprotect()."""

    #     mock_msg.level = 0
    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_unprotect(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_contid.return_value = "123"
    #     mock_uprotcont.return_value = False
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_unprotect(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_contid.return_value = "123"
    #     mock_uprotcont.return_value = True
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_unprotect(self.cmdp)
    #     self.assertEqual(status, 0)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_contid.return_value = ""
    #     mock_uprotimg.return_value = True
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_unprotect(self.cmdp)
    #     self.assertEqual(status, 0)
    #     self.assertTrue(mock_uprotimg.called)

    # @patch('udocker.container.localrepo.LocalRepository.set_container_name', autospec=True)
    # @patch('udocker.container.localrepo.LocalRepository.get_container_id', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.get', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.missing_options', autospec=True)
    # @patch('udocker.cli.UdockerCLI._check_imagespec')
    # @patch('udocker.cli.KeyStore')
    # @patch('udocker.cli.DockerIoAPI')
    # @patch('udocker.cli.Msg')
    # def test_30_do_name(self, mock_msg, mock_dioapi, mock_ks,
    #                     mock_chkimg, mock_miss, mock_get, mock_contid,
    #                     mock_setcont):
    #     """Test30 UdockerCLI().do_name()."""

    #     mock_msg.level = 0
    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_name(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "NAME", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_contid.return_value = ""
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_name(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "NAME", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_contid.return_value = "123"
    #     mock_setcont.return_value = False
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_name(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "NAME", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_contid.return_value = "123"
    #     mock_setcont.return_value = True
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_name(self.cmdp)
    #     self.assertEqual(status, 0)

    # def test_31_do_rename(self):
    #     """Test31 UdockerCLI().do_rename()."""

    # @patch('udocker.container.localrepo.LocalRepository.del_container_name', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.get', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.missing_options', autospec=True)
    # @patch('udocker.cli.UdockerCLI._check_imagespec')
    # @patch('udocker.cli.KeyStore')
    # @patch('udocker.cli.DockerIoAPI')
    # @patch('udocker.cli.Msg')
    # def test_32_do_rmname(self, mock_msg, mock_dioapi, mock_ks,
    #                       mock_chkimg, mock_miss, mock_get, mock_delcontname):
    #     """Test32 UdockerCLI().do_rmname()."""

    #     mock_msg.level = 0
    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_rmname(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["NAME", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_delcontname.return_value = False
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_rmname(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["NAME", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_delcontname.return_value = True
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_rmname(self.cmdp)
    #     self.assertEqual(status, 0)

    # @patch('udocker.container.localrepo.LocalRepository.get_container_id', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.get', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.missing_options', autospec=True)
    # @patch('udocker.cli.ContainerStructure')
    # @patch('udocker.cli.UdockerCLI._check_imagespec')
    # @patch('udocker.cli.KeyStore')
    # @patch('udocker.cli.Msg')
    # def test_33_do_inspect(self, mock_msg,
    #                        mock_ks, mock_chkimg, mock_cstruct, mock_miss,
    #                        mock_get, mock_contid):
    #     """Test33 UdockerCLI().do_inspect()."""

    #     mock_msg.level = 0
    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_inspect(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_contid.return_value = "123"
    #     mock_cstruct.return_value.get_container_attr.return_value = ("", "")
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_inspect(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "PRINT", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_contid.return_value = "123"
    #     mock_cstruct.return_value.get_container_attr.return_value = ("DIR", "")
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_inspect(self.cmdp)
    #     self.assertEqual(status, 0)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_contid.return_value = "123"
    #     mock_cstruct.return_value.get_container_attr.return_value = ("", "JSON")
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_inspect(self.cmdp)
    #     self.assertEqual(status, 0)

    # @patch('udocker.container.localrepo.LocalRepository.verify_image', autospec=True)
    # @patch('udocker.container.localrepo.LocalRepository.cd_imagerepo', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.get', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.missing_options', autospec=True)
    # @patch('udocker.cli.UdockerCLI._check_imagespec')
    # @patch('udocker.cli.KeyStore')
    # @patch('udocker.cli.DockerIoAPI')
    # @patch('udocker.cli.Msg')
    # def test_34_do_verify(self, mock_msg, mock_dioapi,
    #                       mock_ks, mock_chkimg, mock_miss, mock_get,
    #                       mock_cdimgrepo, mock_verifyimg):
    #     """Test34 UdockerCLI().do_verify()."""

    #     mock_msg.level = 0
    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_verify(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("", "")
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_verify(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_cdimgrepo.return_value = False
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_verify(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = False
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_chkimg.return_value = ("IMAGE", "TAG")
    #     mock_cdimgrepo.return_value = True
    #     mock_verifyimg.return_value = True
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_verify(self.cmdp)
    #     self.assertEqual(status, 0)

    # @patch('udocker.container.localrepo.LocalRepository.isprotected_container', autospec=True)
    # @patch('udocker.container.localrepo.LocalRepository.cd_container', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.get', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.missing_options', autospec=True)
    # @patch('udocker.cli.ExecutionMode')
    # @patch('udocker.cli.KeyStore')
    # @patch('udocker.cli.DockerIoAPI')
    # @patch('udocker.cli.Msg')
    # def test_35_do_setup(self, mock_msg, mock_dioapi, mock_ks,
    #                      mock_exec, mock_miss, mock_get, mock_cdcont,
    #                      mock_isprotcont):
    #     """Test35 UdockerCLI().do_setup()."""

    #     mock_msg.level = 0
    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_cdcont.return_value = False
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_setup(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_cdcont.return_value = True
    #     mock_exec.set_mode.return_value = False
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_setup(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     mock_cdcont.return_value = True
    #     mock_exec.set_mode.return_value = True
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_setup(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "P1", "" "", "", ]
    #     mock_cdcont.return_value = True
    #     mock_isprotcont.return_value = True
    #     mock_exec.set_mode.return_value = True
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_setup(self.cmdp)
    #     self.assertEqual(status, 1)

    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "P1", "" "", "", ]
    #     mock_cdcont.return_value = True
    #     mock_isprotcont.return_value = False
    #     mock_exec.set_mode.return_value = True
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_setup(self.cmdp)
    #     self.assertEqual(status, 1)

    # @patch('udocker.cmdparser.CmdParser.get', autospec=True)
    # @patch('udocker.cmdparser.CmdParser.missing_options', autospec=True)
    # @patch('udocker.cli.UdockerTools')
    # @patch('udocker.cli.Msg')
    # def test_36_do_install(self, mock_msg, mock_utools, mock_miss, mock_get):
    #     """Test36 UdockerCLI().do_install()."""

    #     mock_msg.level = 0
    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "", "" "", "", ]
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_install(self.cmdp)
    #     self.assertFalse(mock_utools.return_value.purge.called)
    #     # self.assertTrue(mock_utools.return_value.install.called)

    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "--purge", "" "", "", ]
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_install(self.cmdp)
    #     # self.assertTrue(mock_utools.return_value.purge.called)
    #     self.assertTrue(mock_utools.return_value.install.called_with(False))

    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "--purge", "--force" "", "", ]
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_install(self.cmdp)
    #     # self.assertTrue(mock_utools.return_value.purge.called)
    #     self.assertTrue(mock_utools.return_value.install.called_with(True))

    #     mock_miss.return_value = True
    #     mock_get.side_effect = ["", "", "--force" "", "", ]
    #     udoc = UdockerCLI(self.local)
    #     status = udoc.do_install(self.cmdp)
    #     # self.assertFalse(mock_utools.return_value.purge.called)
    #     self.assertTrue(mock_utools.return_value.install.called_with(True))

    # @patch('udocker.cli.Msg')
    # def test_37_do_showconf(self, mock_msg):
    #     """Test37 UdockerCLI().do_showconf()."""
    #     udoc = UdockerCLI(self.local)
    #     udoc.do_showconf(self.cmdp)
    #     self.assertTrue(mock_msg.return_value.out.called)

    # def test_38_do_version(self):
    #     """Test38 UdockerCLI().do_version()."""
    #     udoc = UdockerCLI(self.local)
    #     version = udoc.do_version(self.cmdp)
    #     self.assertIsNotNone(version)

    # @patch('udocker.cli.Msg')
    # def test_39_do_help(self, mock_msg):
    #     """Test39 UdockerCLI().do_help()."""
    #     udoc = UdockerCLI(self.local)
    #     udoc.do_help(self.cmdp)
    #     self.assertTrue(mock_msg.return_value.out.called)


if __name__ == '__main__':
    main()
