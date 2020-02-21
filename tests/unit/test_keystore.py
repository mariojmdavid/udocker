#!/usr/bin/env python
"""
udocker unit tests: Keystore
"""
import sys
from unittest import TestCase, main
from udocker.helper.keystore import KeyStore
from udocker.config import Config
try:
    from unittest.mock import patch, mock_open
except ImportError:
    from mock import patch, mock_open

if sys.version_info[0] >= 3:
    BUILTINS = "builtins"
else:
    BUILTINS = "__builtin__"


class KeyStoreTestCase(TestCase):
    """Test KeyStore() local basic credentials storage."""

    def setUp(self):
        Config().getconf()

    def tearDown(self):
        pass

    def test_01_init(self):
        """Test01 KeyStore() constructor."""
        kstore = KeyStore("filename")
        status = kstore.keystore_file
        self.assertEqual(status, "filename")

    # def test_02__verify_keystore(self):
    #     """Test02 KeyStore()._verify_keystore()."""

    @patch('udocker.helper.keystore.json.load')
    def test_03__read_all(self, mock_jload):
        """Test03 KeyStore()._read_all()."""
        url = u'https://xxx'
        email = u'user@domain'
        auth = u'xxx'
        credentials = {url: {u'email': email, u'auth': auth}}
        mock_jload.return_value = credentials
        with patch(BUILTINS + '.open', mock_open()):
            kstore = KeyStore("filename")
            status = kstore._read_all()
            self.assertEqual(status, credentials)

    @patch.object(KeyStore, '_verify_keystore')
    @patch('udocker.helper.keystore.FileUtil.size')
    def test_04__shred(self, mock_size, mock_verks):
        """Test04 KeyStore()._shred()."""
        with patch(BUILTINS + '.open', mock_open()):
            kstore = KeyStore("filename")
            status = kstore._shred()
            self.assertEqual(status, 0)

        mock_size.return_value = 123
        with patch(BUILTINS + '.open', mock_open()):
            kstore = KeyStore("filename")
            status = kstore._shred()
            self.assertEqual(status, 0)

    @patch('udocker.helper.keystore.json.dump')
    @patch('udocker.helper.keystore.os.umask')
    def test_05__write_all(self, mock_umask, mock_jdump):
        """Test05 KeyStore()._write_all()."""
        url = u'https://xxx'
        email = u'user@domain'
        auth = u'xxx'
        credentials = {url: {u'email': email, u'auth': auth}}
        mock_umask.return_value = 0o77
        mock_jdump.side_effect = IOError('json dump')
        with patch(BUILTINS + '.open', mock_open()):
            kstore = KeyStore("filename")
            status = kstore._write_all(credentials)
            self.assertEqual(status, 1)

    @patch.object(KeyStore, '_read_all')
    def test_06_get(self, mock_readall):
        """Test06 KeyStore().get()."""
        url = u'https://xxx'
        email = u'user@domain'
        auth = u'xxx'
        credentials = {url: {u'email': email, u'auth': auth}}
        mock_readall.return_value = credentials
        kstore = KeyStore("filename")
        self.assertTrue(kstore.get(url))
        self.assertFalse(kstore.get("NOT EXISTING ENTRY"))

    @patch.object(KeyStore, '_write_all')
    @patch.object(KeyStore, '_read_all')
    def test_07_put(self, mock_readall, mock_writeall):
        """Test07 KeyStore().put()."""
        url = u'https://xxx'
        email = u'user@domain'
        auth = u'xxx'
        credentials = {url: {u'email': email, u'auth': auth}}
        kstore = KeyStore("filename")
        self.assertFalse(kstore.put("", "", ""))

        mock_readall.return_value = dict()
        kstore = KeyStore("filename")
        kstore.put(url, auth, email)
        mock_writeall.assert_called_once_with(credentials)

    @patch.object(KeyStore, '_verify_keystore')
    @patch.object(KeyStore, '_shred')
    @patch.object(KeyStore, '_write_all')
    @patch.object(KeyStore, '_read_all')
    def test_08_delete(self, mock_readall, mock_writeall, mock_shred,
                       mock_verks):
        """Test08 KeyStore().delete()."""
        url = u'https://xxx'
        email = u'user@domain'
        auth = u'xxx'
        credentials = {url: {u'email': email, u'auth': auth}}
        mock_readall.return_value = credentials
        mock_writeall.return_value = 0
        kstore = KeyStore("filename")
        status = kstore.delete(url)
        mock_writeall.assert_called_once_with({})
        self.assertEqual(status, 0)

    @patch('udocker.helper.keystore.os.unlink')
    @patch.object(KeyStore, '_verify_keystore')
    @patch.object(KeyStore, '_shred')
    def test_09_erase(self, mock_shred, mock_verks, mock_unlink):
        """Test09 KeyStore().erase()."""
        kstore = KeyStore("filename")
        self.assertEqual(kstore.erase(), 0)
        mock_unlink.assert_called_once_with("filename")

        mock_unlink.side_effect = IOError
        kstore = KeyStore("filename")
        self.assertEqual(kstore.erase(), 1)


if __name__ == '__main__':
    main()
