#!/usr/bin/env python
"""
udocker unit tests: SingularityEngine
"""

import sys
from unittest import TestCase, main
from udocker.config import Config
from udocker.engine.singularity import SingularityEngine
try:
    from unittest.mock import Mock, patch, MagicMock, mock_open
except ImportError:
    from mock import Mock, patch, MagicMock, mock_open


class SingularityEngineTestCase(TestCase):
    """Test SingularityEngine() class for containers execution."""

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

        str_local = 'udocker.container.localrepo.LocalRepository'
        self.lrepo = patch(str_local)
        self.local = self.lrepo.start()
        self.mock_lrepo = Mock()
        self.local.return_value = self.mock_lrepo

        str_exmode = 'udocker.engine.execmode.ExecutionMode'
        self.execmode = patch(str_exmode)
        self.xmode = self.execmode.start()
        self.mock_execmode = Mock()
        self.xmode.return_value = self.mock_execmode

    def tearDown(self):
        self.lrepo.stop()
        self.execmode.stop()

    @patch('udocker.engine.proot.HostInfo.oskernel')
    def test_01_init(self, mock_kernel):
        """Test01 SingularityEngine() constructor."""
        mock_kernel.return_value = "4.8.13"
        prex = PRootEngine(self.local, self.xmode)
        self.assertFalse(prex.proot_noseccomp)
        self.assertEqual(prex._kernel, "4.8.13")

    @patch('udocker.engine.proot.FileUtil.find_file_in_dir')
    def test_02_select_proot(self, mock_fimage, mock_isgreater):
        """Test02 SingularityEngine().select_proot()."""
        Config().conf['arch'] = "amd64"
        Config().conf['proot_noseccomp'] = None
        mock_isgreater.return_value = False
        mock_fimage.return_value = "proot-4_8_0"
        prex = PRootEngine(self.local, self.xmode)
        prex.select_proot()
        self.assertFalse(prex.proot_noseccomp)



if __name__ == '__main__':
    main()
