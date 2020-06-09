#!/usr/bin/env python
"""
udocker unit tests: UdockerTools
"""

import sys
sys.path.append('.')
sys.path.append('../../')

from unittest import TestCase, main
from udocker.config import Config
from udocker.tools import UdockerTools
try:
    from unittest.mock import Mock, patch, MagicMock, mock_open
except ImportError:
    from mock import Mock, patch, MagicMock, mock_open

if sys.version_info[0] >= 3:
    BUILTINS = "builtins"
else:
    BUILTINS = "__builtin__"

BOPEN = BUILTINS + '.open'


class UdockerToolsTestCase(TestCase):
    """Test UdockerTools()."""

    def setUp(self):
        Config().getconf()
        str_local = 'udocker.container.localrepo.LocalRepository'
        self.lrepo = patch(str_local)
        self.local = self.lrepo.start()
        self.mock_lrepo = Mock()
        self.local.return_value = self.mock_lrepo

    def tearDown(self):
        self.lrepo.stop()

    @patch('udocker.tools.GetURL')
    def test_01_init(self, mock_geturl):
        """Test01 UdockerTools() constructor."""
        mock_geturl.return_value = None
        utools = UdockerTools(self.local)
        self.assertTrue(mock_geturl.called)
        self.assertEqual(utools.localrepo, self.local)

    @patch('udocker.tools.Msg')
    def test_02__instructions(self, mock_msg):
        """Test02 UdockerTools()._instructions()."""
        utools = UdockerTools(self.local)
        utools._instructions()
        self.assertTrue(mock_msg.return_value.out.call_count, 2)

    def test_03__version2int(self):
        """Test03 UdockerTools()._version2int()."""
        utools = UdockerTools(self.local)
        status = utools._version2int("2.4")
        self.assertEqual(status, 2004000)

    def test_04__version_isok(self):
        """Test04 UdockerTools()._version_isok()."""
        Config.conf['tarball_release'] = "1.3"
        utools = UdockerTools(self.local)
        status = utools._version_isok("2.4")
        self.assertTrue(status)

        Config.conf['tarball_release'] = "2.3"
        utools = UdockerTools(self.local)
        status = utools._version_isok("1.4")
        self.assertFalse(status)

    @patch('udocker.tools.FileUtil.getdata')
    def test_05_is_available(self, mock_fuget):
        """Test05 UdockerTools().is_available()."""
        Config.conf['tarball_release'] = "2.3"
        mock_fuget.return_value = "2.3\n"
        utools = UdockerTools(self.local)
        status = utools.is_available()
        self.assertTrue(status)

    @patch('udocker.tools.FileUtil.remove')
    @patch('udocker.tools.FileUtil.register_prefix')
    @patch('udocker.tools.os.listdir')
    def test_06_purge(self, mock_lsdir, mock_fureg, mock_furm):
        """Test06 UdockerTools().purge()."""
        mock_lsdir.side_effect = [["f1", "f2"], ["f3", "f4"]]
        mock_fureg.side_effect = [None, None, None, None]
        mock_furm.side_effect = [None, None, None, None]
        utools = UdockerTools(self.local)
        utools.purge()
        self.assertTrue(mock_lsdir.call_count, 2)
        self.assertTrue(mock_fureg.call_count, 4)
        self.assertTrue(mock_furm.call_count, 4)

    # @patch('udocker.tools.GetURL')
    # @patch('udocker.tools.FileUtil.remove')
    # @patch('udocker.tools.FileUtil.mktmp')
    # def test_07__download(self, mock_fumktmp, mock_furm, mock_geturl):
    #     """Test07 UdockerTools()._download()."""
    #     url = "https://down/file"
    #     mock_fumktmp.return_value = "/tmp/tmpf"
    #     mock_furm.return_value = None
    #     utools = UdockerTools(self.local)
    #     utools.curl = mock_geturl
    #     utools.curl.get = ("HTTP/1.1 200 OK",
    #                        "Content-Type: application/octet-stream")
    #     status = utools._download(url)
    #     self.assertTrue(mock_fumktmp.called)

    # def test_08__get_file(self):
    #     """Test08 UdockerTools()._get_file()."""

    # def test_09__verify_version(self):
    #     """Test09 UdockerTools()._verify_version()."""

    # def test_10__install(self):
    #     """Test10 UdockerTools()._install()."""

    # def test_11__get_mirrors(self):
    #     """Test11 UdockerTools()._get_mirrors()."""

    # def test_12_get_installinfo(self):
    #     """Test12 UdockerTools().get_installinfo()."""

    # def test_13__install_logic(self):
    #     """Test13 UdockerTools()._install_logic()."""

    # def test_14_install(self):
    #     """Test14 UdockerTools().install()."""


if __name__ == '__main__':
    main()
