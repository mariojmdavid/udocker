#!/usr/bin/env python
"""
udocker unit tests: FileUtil
"""
import sys
import os
from unittest import TestCase, main
from udocker.utils.fileutil import FileUtil
from udocker.config import Config
try:
    from unittest.mock import patch, mock_open
except ImportError:
    from mock import patch, mock_open

STDOUT = sys.stdout
STDERR = sys.stderr
UDOCKER_TOPDIR = "test_topdir"
if sys.version_info[0] >= 3:
    BUILTINS = "builtins"
else:
    BUILTINS = "__builtin__"


def find_str(self, find_exp, where):
    """Find string in test output messages."""
    found = False
    for item in where:
        if find_exp in str(item):
            self.assertTrue(True)
            found = True
            break
    if not found:
        self.assertTrue(False)


def is_writable_file(obj):
    """Check if obj is a file."""
    try:
        obj.write("")
    except(AttributeError, OSError, IOError):
        return False
    else:
        return True


class FileUtilTestCase(TestCase):
    """Test FileUtil() file manipulation methods."""

    def setUp(self):
        Config().getconf()
        Config().conf["tmpdir"] = "/tmp"

    def tearDown(self):
        pass

    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_01_init(self, mock_regpre, mock_base, mock_absp):
        """Test01 FileUtil() constructor."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        futil = FileUtil('filename.txt')
        self.assertEqual(futil.filename, os.path.abspath('filename.txt'))
        self.assertTrue(mock_regpre.called)

        futil = FileUtil('-')
        self.assertEqual(futil.filename, '-')
        self.assertEqual(futil.basename, '-')

    # TODO: needs proper implementation and verification
    # @patch('udocker.utils.fileutil.os.path.isdir')
    # @patch('udocker.utils.fileutil.os.path.realpath')
    # def test_02__register_prefix(self, mock_rpath,
    #                              mock_isdir):
    #     """Test02 FileUtil._register_prefix()."""
    #     prefix = "/dir"
    #     res = ["/dir/", "/dir/", "/dir/", "/dir/"]
    #     mock_rpath.return_value = "/dir"
    #     mock_isdir.return_value = True
    #     futil = FileUtil('filename.txt')
    #     futil._register_prefix(prefix)
    #     self.assertEqual(futil.safe_prefixes, res)

    #     prefix = "/dir/"
    #     res = ["/dir/", "/dir/", "/dir/", "/dir/"]
    #     mock_rpath.return_value = "/dir/"
    #     mock_isdir.return_value = False
    #     futil = FileUtil('filename.txt')
    #     futil._register_prefix(prefix)
    #     self.assertEqual(futil.safe_prefixes, res)

    @patch.object(FileUtil, '_register_prefix')
    def test_03_register_prefix(self, mock_regpre):
        """Test03 FileUtil.register_prefix()."""
        mock_regpre.return_value = None
        futil = FileUtil('filename.txt')
        futil.register_prefix()
        self.assertTrue(mock_regpre.called)


    @patch('udocker.utils.fileutil.os.umask')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_04_umask(self, mock_regpre, mock_base,
                      mock_absp, mock_umask):
        """Test04 FileUtil.umask()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_umask.return_value = 0
        futil = FileUtil("somedir")
        status = futil.umask()
        self.assertTrue(status)

        mock_umask.return_value = 0
        futil = FileUtil("somedir")
        FileUtil.orig_umask = 0
        status = futil.umask(1)
        self.assertTrue(status)
        self.assertEqual(FileUtil.orig_umask, 0)

        mock_umask.return_value = 0
        futil = FileUtil("somedir")
        FileUtil.orig_umask = None
        status = futil.umask(1)
        self.assertTrue(status)
        self.assertEqual(FileUtil.orig_umask, 0)

    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_05_mktmp(self, mock_regpre, mock_base, mock_absp):
        """Test05 FileUtil.mktmp()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename2.txt'
        mock_absp.return_value = '/tmp/filename2.txt'
        Config().conf['tmpdir'] = '/somewhere'
        tmp_file = FileUtil('filename2.txt').mktmp()
        self.assertTrue(tmp_file.endswith('-filename2.txt'))
        self.assertTrue(tmp_file.startswith('/somewhere/udocker-'))
        self.assertGreater(len(tmp_file.strip()), 68)

    @patch('udocker.utils.fileutil.os.makedirs')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_06_mkdir(self, mock_regpre, mock_base,
                      mock_absp, mock_mkdirs):
        """Test06 FileUtil.mkdir()"""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_mkdirs.return_value = True
        status = FileUtil("somedir").mkdir()
        self.assertTrue(status)

        mock_mkdirs.side_effect = OSError("fail")
        status = FileUtil("somedir").mkdir()
        self.assertFalse(status)

    @patch('udocker.utils.fileutil.os.rmdir')
    def test_07_rmdir(self, mock_rmdir):
        """Test07 FileUtil.rmdir()."""
        mock_rmdir.return_value = None
        status = FileUtil("somedir").rmdir()
        self.assertTrue(status)

        mock_rmdir.side_effect = OSError("fail")
        status = FileUtil("somedir").rmdir()
        self.assertFalse(status)

    @patch.object(FileUtil, 'mktmp')
    @patch.object(FileUtil, 'mkdir')
    def test_08_mktmpdir(self, mock_mkdir, mock_mktmp):
        """Test08 FileUtil.mktmpdir()."""
        mock_mktmp.return_value = "/dir"
        mock_mkdir.return_value = True
        status = FileUtil("somedir").mktmpdir()
        self.assertEqual(status, "/dir")

        mock_mktmp.return_value = "/dir"
        mock_mkdir.return_value = False
        status = FileUtil("somedir").mktmpdir()
        self.assertEqual(status, None)

    @patch('udocker.utils.fileutil.os.stat')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_09_uid(self, mock_regpre, mock_base,
                    mock_absp, mock_stat):
        """Test09 FileUtil.uid()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_stat.return_value.st_uid = 1234
        Config().conf['tmpdir'] = "/tmp"
        futil = FileUtil("filename.txt")
        uid = futil.uid()
        self.assertEqual(uid, 1234)

        mock_stat.side_effect = OSError("fail")
        Config().conf['tmpdir'] = "/tmp"
        futil = FileUtil("filename.txt")
        uid = futil.uid()
        self.assertEqual(uid, -1)

    @patch('udocker.utils.fileutil.os.path.isdir')
    @patch('udocker.utils.fileutil.os.path.realpath')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_10__is_safe_prefix(self, mock_regpre, mock_base,
                                mock_absp, mock_rpath, mock_isdir):
        """Test10 FileUtil._is_safe_prefix()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_rpath.return_value = '/tmp/filename.txt'
        futil = FileUtil("somedir")
        FileUtil.safe_prefixes = []
        status = futil._is_safe_prefix("/AAA")
        self.assertFalse(status)

        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_rpath.return_value = '/tmp/filename.txt'
        mock_isdir.return_value = True
        futil = FileUtil("somedir")
        FileUtil.safe_prefixes = ["/tmp"]
        status = futil._is_safe_prefix("/tmp/AAA")
        self.assertTrue(status)

    # TODO: The is a bug, calls _chmod, and _chown not implemented
    # @patch.object(FileUtil, '_chmod')
    # @patch('udocker.utils.fileutil.os.walk')
    # @patch('udocker.utils.fileutil.os.lchown')
    # @patch('udocker.utils.fileutil.os.path.abspath')
    # @patch('udocker.utils.fileutil.os.path.basename')
    # @patch.object(FileUtil, '_register_prefix')
    # def test_11_chown(self, mock_regpre, mock_base,
    #                   mock_absp, mock_lchown, mock_walk,
    #                   mock_fuchmod):
    #     """Test11 FileUtil.chown()."""
    #     mock_regpre.return_value = None
    #     mock_base.return_value = 'filename.txt'
    #     mock_absp.return_value = '/tmp/filename.txt'
    #     mock_walk.return_value = [("/tmp", ["dir"], ["file"]), ]
    #     mock_lchown.side_effect = [None, None, None, None]
    #     mock_fuchmod.return_value = None
    #     futil = FileUtil("somedir")
    #     FileUtil.safe_prefixes = ["/tmp"]
    #     status = futil.chown(0, 0, False)
    #     self.assertTrue(status)
    #     self.assertTrue(mock_fuchmod.called)
    #     self.assertFalse(mock_walk.called)

    #     mock_regpre.return_value = None
    #     mock_base.return_value = 'filename.txt'
    #     mock_absp.return_value = '/tmp/filename.txt'
    #     mock_walk.return_value = [("/tmp", ["dir"], ["file"]), ]
    #     mock_lchown.side_effect = [None, None, None, None]
    #     mock_fuchmod.return_value = None
    #     futil = FileUtil("somedir")
    #     FileUtil.safe_prefixes = ["/tmp"]
    #     status = futil.chown(0, 0, True)
    #     self.assertTrue(status)
    #     self.assertTrue(mock_fuchmod.called)
    #     self.assertTrue(mock_walk.called)
    #     self.assertTrue(mock_lchown.called)

    #     mock_regpre.return_value = None
    #     mock_base.return_value = 'filename.txt'
    #     mock_absp.return_value = '/tmp/filename.txt'
    #     mock_walk.return_value = [("/tmp", ["dir"], ["file"]), ]
    #     mock_lchown.side_effect = [None, None, None, None]
    #     mock_fuchmod.side_effect = OSError("fail")
    #     futil = FileUtil("somedir")
    #     FileUtil.safe_prefixes = ["/tmp"]
    #     status = futil.chown(0, 0, False)
    #     self.assertFalse(status)

    @patch.object(FileUtil, 'chown')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_12_rchown(self, mock_regpre, mock_base,
                       mock_absp, mock_fuchown):
        """Test12 FileUtil.rchown()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_fuchown.return_value = True
        futil = FileUtil("somedir")
        FileUtil.safe_prefixes = ["/tmp"]
        status = futil.rchown()
        self.assertTrue(status)

    @patch('udocker.utils.fileutil.Msg.err')
    @patch('udocker.utils.fileutil.stat')
    @patch('udocker.utils.fileutil.os.chmod')
    @patch('udocker.utils.fileutil.os.lstat')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_13__chmod(self, mock_regpre, mock_base,
                       mock_absp, mock_lstat, mock_chmod,
                       mock_stat, mock_msgerr):
        """Test13 FileUtil._chmod()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_lstat.return_value.st_mode = 33277
        mock_chmod.return_value = None
        mock_stat.return_value.S_ISREG = True
        mock_stat.return_value.S_IMODE = 509
        futil = FileUtil("somedir")
        futil._chmod("somefile")
        self.assertTrue(mock_lstat.called)
        self.assertTrue(mock_stat.S_ISREG.called)
        self.assertTrue(mock_stat.S_IMODE.called)

        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_lstat.return_value.st_mode = 33277
        mock_chmod.return_value = None
        mock_stat.return_value.S_ISREG = False
        mock_stat.return_value.S_ISDIR = True
        mock_stat.return_value.S_IMODE = 509
        futil = FileUtil("somedir")
        futil._chmod("somefile")
        self.assertTrue(mock_chmod.called)
        self.assertTrue(mock_stat.S_IMODE.called)

    @patch.object(FileUtil, '_chmod')
    @patch('udocker.utils.fileutil.os.walk')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test14_chmod(self, mock_regpre, mock_base,
                      mock_absp, mock_walk, mock_fuchmod):
        """Test14 FileUtil.chmod()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_walk.return_value = [("/tmp", ["dir"], ["file"]), ]
        mock_fuchmod.return_value = None
        futil = FileUtil("somedir")
        FileUtil.safe_prefixes = ["/tmp"]
        status = futil.chmod(0o600, 0o700, 0o755, False)
        self.assertTrue(status)
        self.assertTrue(mock_fuchmod.called)
        self.assertFalse(mock_walk.called)

        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_walk.return_value = [("/tmp", ["dir"], ["file"]), ]
        mock_fuchmod.side_effect = [None, None, None, None]
        futil = FileUtil("somedir")
        FileUtil.safe_prefixes = ["/tmp"]
        status = futil.chmod(0o600, 0o700, 0o755, True)
        self.assertTrue(status)
        self.assertTrue(mock_fuchmod.called)
        self.assertTrue(mock_walk.called)

        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_walk.return_value = [("/tmp", ["dir"], ["file"]), ]
        mock_fuchmod.side_effect = OSError("fail")
        futil = FileUtil("somedir")
        FileUtil.safe_prefixes = ["/tmp"]
        status = futil.chmod(0o600, 0o700, 0o755, False)
        self.assertFalse(status)

    @patch.object(FileUtil, 'chmod')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_15_rchmod(self, mock_regpre, mock_base,
                       mock_absp, mock_fuchmod):
        """Test15 FileUtil.rchmod()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_fuchmod.return_value = True
        futil = FileUtil("somedir")
        FileUtil.safe_prefixes = ["/tmp"]
        futil.rchmod()
        self.assertTrue(mock_fuchmod.called)

    @patch('udocker.utils.fileutil.os.rmdir')
    @patch('udocker.utils.fileutil.os.unlink')
    @patch('udocker.utils.fileutil.os.chmod')
    @patch('udocker.utils.fileutil.os.walk')
    @patch('udocker.utils.fileutil.os.path.islink')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_16__removedir(self, mock_regpre, mock_base, mock_absp,
                           mock_islink, mock_walk, mock_chmod,
                           mock_unlink, mock_rmdir):
        """Test16 FileUtil._removedir()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_walk.return_value = [("/tmp", ["dir"], ["file"]), ]
        mock_islink.side_effect = [False, True, True, True]
        mock_chmod.side_effect = [None, None, None, None]
        mock_unlink.side_effect = [None, None, None, None]
        mock_rmdir.side_effect = [None, None, None, None]
        # remove directory under /tmp OK
        futil = FileUtil("/tmp/directory")
        status = futil._removedir()
        self.assertTrue(mock_walk.called)
        self.assertTrue(mock_islink.call_count, 2)
        self.assertTrue(mock_chmod.call_count, 3)
        self.assertTrue(status)

        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_walk.return_value = list()
        mock_chmod.side_effect = OSError("fail")
        futil = FileUtil("/directory")
        status = futil._removedir()
        self.assertFalse(status)


    @patch('udocker.utils.fileutil.os.path.realpath')
    @patch('udocker.utils.fileutil.os.path.exists')
    @patch('udocker.utils.fileutil.Msg')
    @patch('udocker.utils.fileutil.os.remove')
    @patch('udocker.utils.fileutil.os.path.islink')
    @patch('udocker.utils.fileutil.os.path.isfile')
    @patch('udocker.utils.fileutil.os.path.isdir')
    @patch.object(FileUtil, 'uid')
    @patch.object(FileUtil, '_is_safe_prefix')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_17_remove(self, mock_regpre, mock_base, mock_absp, mock_safe,
                       mock_uid, mock_isdir,
                       mock_isfile, mock_islink, mock_remove, mock_msg,
                       mock_exists, mock_realpath):
        """Test17 FileUtil.remove() with plain files."""
        mock_regpre.return_value = None
        mock_base.return_value = '/filename4.txt'
        mock_absp.return_value = '/filename4.txt'
        mock_uid.return_value = 1000
        # file does not exist (regression of #50)
        mock_isdir.return_value = True
        mock_isfile.return_value = True
        mock_exists.return_value = True
        mock_safe.return_value = True
        Config().conf['uid'] = 1000
        Config().conf['tmpdir'] = "/tmp"
        mock_realpath.return_value = "/tmp"
        # under /
        futil = FileUtil("/filename4.txt")
        status = futil.remove()
        self.assertFalse(status)

        # wrong uid
        mock_base.return_value = 'filename4.txt'
        mock_absp.return_value = '/tmp/filename4.txt'
        mock_uid.return_value = 1001
        futil = FileUtil("/tmp/filename4.txt")
        status = futil.remove()
        self.assertFalse(status)

        # under /tmp
        mock_base.return_value = 'filename4.txt'
        mock_absp.return_value = '/tmp/filename4.txt'
        mock_uid.return_value = 1000
        futil = FileUtil("/tmp/filename4.txt")
        status = futil.remove()
        self.assertTrue(status)

        # under user home
        mock_base.return_value = 'filename4.txt'
        mock_absp.return_value = '/home/user/.udocker/filename4.txt'
        futil = FileUtil("/home/user/.udocker/filename4.txt")
        futil.safe_prefixes.append("/home/user/.udocker")
        status = futil.remove()
        self.assertTrue(status)

        # outside of scope 1
        mock_base.return_value = 'filename4.txt'
        mock_absp.return_value = '/etc/filename4.txt'
        mock_safe.return_value = False
        futil = FileUtil("/etc/filename4.txt")
        futil.safe_prefixes = []
        status = futil.remove()
        self.assertFalse(status)


    @patch('udocker.utils.fileutil.Msg')
    @patch('udocker.utils.fileutil.Uprocess.call')
    @patch('udocker.utils.fileutil.os.path.isfile')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_17_verify_tar(self, mock_regpre, mock_base, mock_absp,
                           mock_isfile, mock_call, mock_msg):
        """Test17 FileUtil.verify_tar()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_msg.level = 0
        mock_msg.VER = 4
        mock_isfile.return_value = False
        mock_call.return_value = 0
        status = FileUtil("tarball.tar").verify_tar()
        self.assertFalse(status)

        mock_isfile.return_value = True
        mock_call.return_value = 0
        status = FileUtil("tarball.tar").verify_tar()
        self.assertTrue(status)

        mock_isfile.return_value = True
        mock_call.return_value = 1
        status = FileUtil("tarball.tar").verify_tar()
        self.assertFalse(status)

    # def test_18_tar(self):
    #     """Test18 FileUtil.tar()."""

    # def test_19_copydir(self):
    #     """Test19 FileUtil.copydir()."""

    @patch.object(FileUtil, 'remove')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_20_cleanup(self, mock_regpre, mock_base, mock_absp, mock_remove):
        """Test20 FileUtil.cleanup() delete tmp files."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        Config().conf['tmpdir'] = "/tmp"
        FileUtil.tmptrash = {'file1.txt': None, 'file2.txt': None}
        FileUtil("").cleanup()
        self.assertEqual(mock_remove.call_count, 2)

    # def test_21_isdir(self):
    #     """Test21 FileUtil.isdir()."""

    @patch('udocker.utils.fileutil.os.stat')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_22_size(self, mock_regpre, mock_base, mock_absp, mock_stat):
        """Test22 FileUtil.size()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_stat.return_value.st_size = 4321
        size = FileUtil("somefile").size()
        self.assertEqual(size, 4321)

    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_23_getdata(self, mock_regpre, mock_base, mock_absp):
        """Test23 FileUtil.getdata()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        with patch(BUILTINS + '.open', mock_open(read_data='qwerty')):
            data = FileUtil("somefile").getdata()
            self.assertEqual(data, 'qwerty')

    # def test_24_get1stline(self):
    #     """Test24 FileUtil.get1stline()."""

    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_25_putdata(self, mock_regpre, mock_base, mock_absp):
        """Test25 FileUtil.putdata()"""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        futil = FileUtil("somefile")
        futil.filename = ""
        data = futil.putdata("qwerty")
        self.assertFalse(data)

        with patch(BUILTINS + '.open', mock_open()):
            data = FileUtil("somefile").putdata("qwerty")
            self.assertEqual(data, 'qwerty')

    # def test_26_getvalid_path(self):
    #     """Test26 FileUtil.getvalid_path()."""

    # def test_27__cont2host(self):
    #     """Test27 FileUtil._cont2host()."""

    # def test_28_cont2host(self):
    #     """Test28 FileUtil.cont2host()."""

    @patch('udocker.utils.fileutil.Uprocess.get_output')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_29_find_exec(self, mock_regpre, mock_base, mock_absp, mock_gout):
        """Test29 FileUtil.find_exec()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_gout.return_value = None
        filename = FileUtil("executable").find_exec()
        self.assertEqual(filename, "")

        # mock_gout.return_value = "/bin/ls"
        # filename = FileUtil("executable").find_exec()
        # self.assertEqual(filename, "/bin/ls")

        mock_gout.return_value = "not found"
        filename = FileUtil("executable").find_exec()
        self.assertEqual(filename, "")

    # def test_30_rename(self):
    #     """Test30 FileUtil.rename()."""

    # def test_31__stream2file(self):
    #     """Test31 FileUtil._stream2file()."""

    # def test_32__file2stream(self):
    #     """Test32 FileUtil._file2stream()."""

    # def test_33__file2file(self):
    #     """Test33 FileUtil._file2file()."""

    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_34_copyto(self, mock_regpre, mock_base, mock_absp):
        """Test34 FileUtil.copyto()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        with patch(BUILTINS + '.open', mock_open()):
            status = FileUtil("source").copyto("dest")
            self.assertTrue(status)

            status = FileUtil("source").copyto("dest", "w")
            self.assertTrue(status)

            status = FileUtil("source").copyto("dest", "a")
            self.assertTrue(status)

    @patch('udocker.utils.fileutil.os.path.exists')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_35_find_file_in_dir(self, mock_regpre, mock_base, mock_absp,
                                 mock_exists):
        """Test35 FileUtil.find_file_in_dir()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/dir'
        file_list = []
        status = FileUtil("/dir").find_file_in_dir(file_list)
        self.assertEqual(status, "")

        file_list = ["F1", "F2"]
        mock_exists.side_effect = [False, False]
        status = FileUtil("/dir").find_file_in_dir(file_list)
        self.assertEqual(status, "")

        file_list = ["F1", "F2"]
        mock_exists.side_effect = [False, True]
        status = FileUtil("/dir").find_file_in_dir(file_list)
        self.assertEqual(status, "/dir/F2")

    @patch('udocker.utils.fileutil.os.stat')
    @patch('udocker.utils.fileutil.os.symlink')
    @patch('udocker.utils.fileutil.os.remove')
    @patch('udocker.utils.fileutil.os.chmod')
    @patch('udocker.utils.fileutil.os.access')
    @patch('udocker.utils.fileutil.os.path.realpath')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_36__link_change_apply(self, mock_regpre, mock_base, mock_absp,
                                   mock_realpath, mock_access, mock_chmod,
                                   mock_remove, mock_symlink, mock_stat):
        """Test36 FileUtil._link_change_apply()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_realpath.return_value = "/HOST/DIR"
        mock_access.return_value = True
        futil = FileUtil("/con")
        futil._link_change_apply("/con/lnk_new", "/con/lnk", False)
        self.assertTrue(mock_remove.called)
        self.assertTrue(mock_symlink.called)

        # Needs reviewing for python3
        if sys.version_info[0] < 3:
            mock_access.return_value = False
            mock_chmod.return_value = None
            mock_remove.return_value = None
            mock_symlink.return_value = None
            mock_realpath.return_value = "/HOST/DIR"
            futil = FileUtil("/con")
            futil._link_change_apply("/con/lnk_new", "/con/lnk", True)
            self.assertTrue(mock_chmod.called)
            self.assertTrue(mock_remove.called)
            self.assertTrue(mock_symlink.called)

    @patch('udocker.utils.fileutil.os.access')
    @patch('udocker.utils.fileutil.os.readlink')
    @patch.object(FileUtil, '_link_change_apply', return_value=None)
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_37__link_set(self, mock_regpre, mock_base, mock_absp,
                          mock_lnchange, mock_readlink, mock_access):
        """Test37 FileUtil._link_set()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_readlink.return_value = "X"
        futil = FileUtil("/con")
        status = futil._link_set("/con/lnk", "", "/con", False)
        self.assertFalse(status)

        mock_readlink.return_value = "/con"
        futil = FileUtil("/con")
        status = futil._link_set("/con/lnk", "", "/con", False)
        self.assertFalse(status)

        mock_readlink.return_value = "/HOST/DIR"
        futil = FileUtil("/con")
        status = futil._link_set("/con/lnk", "", "/con", False)
        self.assertTrue(mock_lnchange.called)
        self.assertTrue(status)

        mock_readlink.return_value = "/HOST/DIR"
        mock_access.return_value = True
        futil = FileUtil("/con")
        status = futil._link_set("/con/lnk", "", "/con", True)
        self.assertTrue(mock_lnchange.called)
        self.assertTrue(status)

        mock_readlink.return_value = "/HOST/DIR"
        mock_access.return_value = False
        futil = FileUtil("/con")
        status = futil._link_set("/con/lnk", "", "/con", True)
        self.assertTrue(mock_lnchange.called)
        self.assertTrue(status)

    @patch('udocker.utils.fileutil.os.access')
    @patch('udocker.utils.fileutil.os.readlink')
    @patch.object(FileUtil, '_link_change_apply', return_value=None)
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_38__link_restore(self, mock_regpre, mock_base, mock_absp,
                              mock_lnchange, mock_readlink, mock_access):
        """Test38 FileUtil._link_restore()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_readlink.return_value = "/con/AAA"
        futil = FileUtil("/con")
        status = futil._link_restore("/con/lnk", "/con", "/root", False)
        self.assertTrue(status)

        mock_readlink.return_value = "/con/AAA"
        futil = FileUtil("/con")
        status = futil._link_restore("/con/lnk", "/con", "/root", False)
        self.assertTrue(mock_lnchange.called)
        self.assertTrue(status)

        mock_readlink.return_value = "/root/BBB"
        futil = FileUtil("/con")
        status = futil._link_restore("/con/lnk", "/con", "/root", False)
        self.assertTrue(mock_lnchange.called)
        self.assertTrue(status)

        mock_readlink.return_value = "/XXX"
        futil = FileUtil("/con")
        status = futil._link_restore("/con/lnk", "/con", "/root", False)
        self.assertTrue(mock_lnchange.called)
        self.assertFalse(status)

        mock_readlink.return_value = "/root/BBB"
        futil = FileUtil("/con")
        status = futil._link_restore("/con/lnk", "/con", "/root", True)
        self.assertTrue(mock_lnchange.called)
        self.assertTrue(status)

        mock_readlink.return_value = "/root/BBB"
        mock_access.return_value = False
        futil = FileUtil("/con")
        status = futil._link_restore("/con/lnk", "", "/root", True)
        self.assertTrue(mock_lnchange.called)
        self.assertTrue(status)

    @patch.object(FileUtil, '_link_restore')
    @patch.object(FileUtil, '_link_set')
    @patch('udocker.utils.fileutil.Msg')
    @patch.object(FileUtil, '_is_safe_prefix')
    @patch('udocker.utils.fileutil.os.lstat')
    @patch('udocker.utils.fileutil.os.path.islink')
    @patch('udocker.utils.fileutil.os.walk')
    @patch('udocker.utils.fileutil.os.path.realpath')
    @patch('udocker.utils.fileutil.os.path.abspath')
    @patch('udocker.utils.fileutil.os.path.basename')
    @patch.object(FileUtil, '_register_prefix')
    def test_39_links_conv(self, mock_regpre, mock_base, mock_absp,
                           mock_realpath, mock_walk, mock_islink,
                           mock_lstat, mock_is_safe_prefix, mock_msg,
                           mock_link_set, mock_link_restore):
        """Test39 FileUtil.links_conv()."""
        mock_regpre.return_value = None
        mock_base.return_value = 'filename.txt'
        mock_absp.return_value = '/tmp/filename.txt'
        mock_realpath.return_value = "/ROOT"
        mock_is_safe_prefix.return_value = False
        futil = FileUtil("/ROOT")
        status = futil.links_conv(False, True, "")
        self.assertEqual(status, None)

        mock_realpath.return_value = "/ROOT"
        mock_is_safe_prefix.return_value = True
        mock_walk.return_value = []
        futil = FileUtil("/ROOT")
        status = futil.links_conv(False, True, "")
        self.assertEqual(status, [])

        mock_realpath.return_value = "/ROOT"
        mock_is_safe_prefix.return_value = True
        mock_walk.return_value = [("/", [], []), ]
        futil = FileUtil("/ROOT")
        status = futil.links_conv(False, True, "")
        self.assertEqual(status, [])

        mock_realpath.return_value = "/ROOT"
        mock_is_safe_prefix.return_value = True
        mock_islink = False
        mock_walk.return_value = [("/", [], ["F1", "F2"]), ]
        futil = FileUtil("/ROOT")
        status = futil.links_conv(False, True, "")
        self.assertEqual(status, [])

        mock_realpath.return_value = "/ROOT"
        mock_is_safe_prefix.return_value = True
        mock_islink = True
        mock_lstat.return_value.st_uid = 1
        Config().conf['uid'] = 0
        mock_walk.return_value = [("/", [], ["F1", "F2"]), ]
        futil = FileUtil("/ROOT")
        status = futil.links_conv(False, True, "")
        self.assertEqual(status, [])

        mock_realpath.return_value = "/ROOT"
        mock_is_safe_prefix.return_value = True
        mock_islink = True
        mock_lstat.return_value.st_uid = 1
        mock_link_set.reset_mock()
        mock_link_restore.reset_mock()
        Config().conf['uid'] = 1
        mock_walk.return_value = [("/", [], ["F1", "F2"]), ]
        futil = FileUtil("/ROOT")
        status = futil.links_conv(False, True, "")
        self.assertFalse(mock_link_restore.called)

        mock_realpath.return_value = "/ROOT"
        mock_is_safe_prefix.return_value = True
        mock_islink = True
        mock_lstat.return_value.st_uid = 1
        mock_link_set.reset_mock()
        mock_link_restore.reset_mock()
        Config().conf['uid'] = 1
        mock_walk.return_value = [("/", [], ["F1", "F2"]), ]
        futil = FileUtil("/ROOT")
        status = futil.links_conv(False, False, "")
        self.assertFalse(mock_link_set.called)

    # def test_40_match(self):
    #     """Test40 FileUtil.match()."""


if __name__ == '__main__':
    main()
