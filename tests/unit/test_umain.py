#!/usr/bin/env python
"""
udocker unit tests: UMain
"""

from unittest import TestCase, main
from udocker.umain import UMain
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class UMainTestCase(TestCase):
    """Test UMain() class main udocker program."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('udocker.umain.sys.exit')
    @patch('udocker.umain.os')
    @patch('udocker.umain.UdockerCLI')
    @patch('udocker.umain.LocalRepository')
    @patch('udocker.umain.Config')
    @patch('udocker.umain.CmdParser')
    @patch('udocker.umain.Msg')
    def test_01_init(self, mock_msg, mock_cmdp, mock_conf,
                     mock_local, mock_cli, mock_os, mock_exit):
        """Test01 UMain(argv) constructor."""

        # mock_cmdp.return_value.get.side_effect call order
        # --allow-root --config --debug    -D
        # --quiet      -q       --insecure --repo
        argv = ['udocker']
        conf = mock_conf.getconf()
        conf['verbose_level'] = 3
        mock_cmdp.return_value.parse.return_value = True

        # Test with no cmd options
        mock_cmdp.return_value.get.side_effect = [False, False, False, False,
                                                  False, False, False, False]
        UMain(argv)
        # self.assertTrue(mock_cmdp.called)
        # self.assertTrue(mock_conf.called)
        self.assertTrue(mock_conf.getconf.called)
        self.assertTrue(mock_msg.setlevel.called_with(conf['verbose_level']))
        # self.assertTrue(mock_local.called)
        # self.assertTrue(mock_cli.called)

        # Test root with no --allow-root
        mock_cmdp.return_value.get.side_effect = [False, False, False, False,
                                                  False, False, False, False]
        mock_os.geteuid.return_value = 0
        UMain(argv)
        # self.assertTrue(mock_exit.called)

        # Test root with --allow-root
        mock_cmdp.return_value.get.side_effect = [True, False, False, False,
                                                  False, False, False, False]
        mock_os.geteuid.return_value = 0
        UMain(argv)
        self.assertFalse(mock_exit.called)
        mock_exit.reset_mock()
        mock_conf.reset_mock()

        # Test --debug
        mock_cmdp.return_value.get.side_effect = [False, False, True, False,
                                                  False, False, False, False]
        UMain(argv)
        #self.assertEqual(confget['verbose_level'], 5)

    # @patch('udocker.umain.sys.exit')
    # @patch('udocker.umain.os')
    # @patch('udocker.umain.UdockerCLI.do_version')
    # @patch('udocker.umain.UdockerCLI.do_listconf')
    # @patch('udocker.umain.UdockerCLI.do_help')
    # @patch('udocker.umain.LocalRepository')
    # @patch('udocker.umain.Config')
    # @patch('udocker.umain.CmdParser')
    # @patch('udocker.umain.Msg')
    # def test_02__prepare_exec(self, mock_msg, mock_cmdp, mock_conf,
    #                           mock_local, mock_help, mock_lconf, mock_ver,
    #                           mock_os, mock_exit):
    #     """Test02 UMain()._prepare_exec()."""
    #     argv = ['udocker']
    #     mock_help.return_value = 0
    #     um = UMain(argv)
    #     status = um._prepare_exec()
    #     self.assertEqual(status, 0)
    #     self.assertTrue(mock_help.called)

    #     argv = ['udocker', 'listconf']
    #     mock_lconf.return_value = 0
    #     um = UMain(argv)
    #     status = um._prepare_exec()
    #     self.assertEqual(status, 0)
    #     self.assertTrue(mock_lconf.called)

    #     argv = ['udocker', 'version']
    #     mock_ver.return_value = 0
    #     um = UMain(argv)
    #     status = um._prepare_exec()
    #     self.assertEqual(status, 0)
    #     self.assertTrue(mock_ver.called)

    # @patch.object(UMain, '_prepare_exec')
    # @patch('udocker.umain.sys.exit')
    # def test_03_execute(self, mock_exit, mock_exec):
    #     """Test03 UMain().execute()."""
    #     argv = ['udocker']
    #     mock_exec.return_value = 0
    #     um = UMain(argv)
    #     status = um.execute()
    #     #self.assertEqual(status, mock_exit)
    #     self.assertTrue(mock_exec.called)
    #     mock_exit.reset_mock()

        # TODO: test the try except clause
        # mock_exec.return_value = 1
        # um = UMain(argv)
        # mock_exec.side_effect = SystemExit()
        # status = um.execute()
        # with self.assertRaises(SystemExit):
        #     # self.assertEqual(status, 1)
        #     self.assertTrue(mock_exit.called)


if __name__ == '__main__':
    main()
