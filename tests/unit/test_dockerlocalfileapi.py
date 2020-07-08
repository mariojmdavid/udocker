#!/usr/bin/env python
"""
udocker unit tests: DockerLocalFileAPI
"""
import sys
sys.path.append('.')
sys.path.append('../../')

from unittest import TestCase, main
from udocker.docker import DockerLocalFileAPI
from udocker.config import Config
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class DockerLocalFileAPITestCase(TestCase):
    """Test DockerLocalFileAPI() manipulate Docker images."""

    def setUp(self):
        Config().getconf()
        str_local = 'udocker.container.localrepo.LocalRepository'
        self.lrepo = patch(str_local)
        self.local = self.lrepo.start()
        self.mock_lrepo = Mock()
        self.local.return_value = self.mock_lrepo

    def tearDown(self):
        self.lrepo.stop()

    def test_01_init(self):
        """Test01 DockerLocalFileAPI() constructor."""
        dlocapi = DockerLocalFileAPI(self.local)
        self.assertEqual(dlocapi.localrepo, self.local)

    @patch('udocker.docker.os.listdir')
    @patch('udocker.docker.FileUtil.isdir')
    def test_02__load_structure(self, mock_isdir, mock_ldir):
        """Test02 DockerLocalFileAPI()._load_structure()."""
        res = {'repoconfigs': {}, 'repolayers': {}}
        mock_ldir.return_value = ["xx"]
        dlocapi = DockerLocalFileAPI(self.local)
        structure = dlocapi._load_structure("/tmp")
        self.assertEqual(structure, res)

        mock_isdir.return_value = False
        mock_ldir.return_value = ["repositories", ]
        self.local.load_json.return_value = {"REPO": "", }
        dlocapi = DockerLocalFileAPI(self.local)
        structure = dlocapi._load_structure("/tmp")
        res = {'repolayers': {}, 'repoconfigs': {},
               'repositories': {'REPO': ''}}
        self.assertEqual(structure, res)

        mock_isdir.return_value = False
        mock_ldir.return_value = ["manifest.json", ]
        dlocapi = DockerLocalFileAPI(self.local)
        structure = dlocapi._load_structure("/tmp")
        res = {'repolayers': {}, 'repoconfigs': {},
               'manifest': {'REPO': ''}}
        self.assertEqual(structure, res)

        jfname = "x" * 70 + ".json"
        res = {"repolayers": {},
               "repoconfigs": {jfname: {"json": {"k": "v"}, 
                                        "json_f": "/tmp/"+jfname}}}
        mock_isdir.return_value = False
        mock_ldir.return_value = [jfname, ]
        self.local.load_json.return_value = {"k": "v"}
        dlocapi = DockerLocalFileAPI(self.local)
        structure = dlocapi._load_structure("/tmp")
        self.assertEqual(structure, res)

        fname = "x" * 64
        res = {"repolayers": {fname: {"VERSION": {"k": "v"}}},
               "repoconfigs": dict()}
        mock_isdir.return_value = True
        mock_ldir.side_effect = [[fname, ], ["VERSION", ], ]
        self.local.load_json.return_value = {"k": "v"}
        dlocapi = DockerLocalFileAPI(self.local)
        structure = dlocapi._load_structure("/tmp")
        self.assertEqual(structure, res)

        fname = "x" * 64
        fulllayer = "/tmp/" + fname + "/json"
        res = {"repolayers": {fname: {"json": {"k": "v"},
                                      "json_f": fulllayer}},
               "repoconfigs": dict()}
        mock_isdir.return_value = True
        mock_ldir.side_effect = [[fname, ], ["json", ], ]
        self.local.load_json.return_value = {"k": "v"}
        dlocapi = DockerLocalFileAPI(self.local)
        structure = dlocapi._load_structure("/tmp")
        self.assertEqual(structure, res)

        fname = "x" * 64
        fulllayer = "/tmp/" + fname + "/layer1"
        res = {"repolayers": {fname: {"layer_f": fulllayer}},
               "repoconfigs": dict()}
        mock_isdir.return_value = True
        mock_ldir.side_effect = [[fname, ], ["layer1", ], ]
        self.local.load_json.return_value = {"k": "v"}
        dlocapi = DockerLocalFileAPI(self.local)
        structure = dlocapi._load_structure("/tmp")
        self.assertEqual(structure, res)

    def test_03__find_top_layer_id(self):
        """Test03 DockerLocalFileAPI()._find_top_layer_id()."""
        fname = "x" * 64
        fulllayer = "/tmp/" + fname + "/layer1"
        structure = dict()
        dlocapi = DockerLocalFileAPI(self.local)
        structure = dlocapi._find_top_layer_id(structure)
        self.assertEqual(structure, "")

        lid = "12345"
        fulllayer = "/tmp/" + lid + "/json"
        struc = {"repolayers": {lid: {"json": {"parent": "v1"},
                                      "json_f": fulllayer}},
                 "repoconfigs": dict()}
        dlocapi = DockerLocalFileAPI(self.local)
        status = dlocapi._find_top_layer_id(struc, "v1")
        self.assertEqual(status, lid)

    def test_04__sorted_layers(self):
        """Test04 DockerLocalFileAPI()._sorted_layers()."""
        lid = "12345"
        fulllayer = "/tmp/" + lid + "/json"
        struc = {"repolayers": {lid: {"json": {"layer": lid},
                                      "json_f": fulllayer}},
                 "repoconfigs": dict()}
        dlocapi = DockerLocalFileAPI(self.local)
        status = dlocapi._sorted_layers(struc, lid)
        self.assertEqual(status, [lid])

    def test_05__get_from_manifest(self):
        """Test05 DockerLocalFileAPI()._get_from_manifest()."""
        struc = dict()
        imgtag = "image:tag"
        dlocapi = DockerLocalFileAPI(self.local)
        status = dlocapi._get_from_manifest(struc, imgtag)
        self.assertEqual(status, ("", []))

        imgtag = "IMAGE"
        struc = {"manifest": [{"RepoTags": {"IMAGE": {"TAG": "tag"}},
                               "Layers": ["l1", "l2"],
                               "Config": "conf"}]}
        dlocapi = DockerLocalFileAPI(self.local)
        status = dlocapi._get_from_manifest(struc, imgtag)
        self.assertEqual(status, ("conf", ["l2", "l1"]))

    # def test_06__load_image_step2(self):
    #     """Test06 DockerLocalFileAPI()._load_image_step2()."""
    #     dlocapi = DockerLocalFileAPI(self.local)

    @patch('udocker.docker.CommonLocalFileApi._load_image')
    def test_07__load_repositories(self, mock_loadi):
        """Test07 DockerLocalFileAPI()._load_repositories()."""
        struct = dict()
        dlocapi = DockerLocalFileAPI(self.local)
        status = dlocapi._load_repositories(struct)
        self.assertFalse(status)

        struct = {"repositories": dict()}
        dlocapi = DockerLocalFileAPI(self.local)
        status = dlocapi._load_repositories(struct)
        self.assertEqual(status, list())

        structure = {"repositories": {"IMAGE": {"TAG": "tag", }, }, }
        mock_loadi.return_value = ["image:tag"]
        dlocapi = DockerLocalFileAPI(self.local)
        status = dlocapi._load_repositories(structure)
        self.assertEqual(status, ["image:tag"])

    @patch.object(DockerLocalFileAPI, '_load_repositories')
    @patch.object(DockerLocalFileAPI, '_load_structure')
    @patch.object(DockerLocalFileAPI, '_untar_saved_container')
    @patch('udocker.docker.os.makedirs')
    @patch('udocker.docker.FileUtil.mktmp')
    @patch('udocker.docker.os.path.exists')
    def test_08_load(self, mock_exists, mock_mktmp,
                     mock_makedirs, mock_untar, mock_lstruct, mock_lrepo):
        """Test08 DockerLocalFileAPI().load()."""
        mock_exists.return_value = False
        mock_mktmp.return_value = "tmpfile"
        dlocapi = DockerLocalFileAPI(self.local)
        status = dlocapi.load("IMAGEFILE")
        self.assertFalse(status)

        mock_exists.return_value = True
        mock_mktmp.return_value = "tmpfile"
        mock_untar.return_value = False
        dlocapi = DockerLocalFileAPI(self.local)
        status = dlocapi.load("IMAGEFILE")
        self.assertFalse(status)

        mock_exists.return_value = True
        mock_mktmp.return_value = "tmpfile"
        mock_untar.return_value = True
        structure = {}
        mock_lstruct.return_value = structure
        dlocapi = DockerLocalFileAPI(self.local)
        status = dlocapi.load("IMAGEFILE")
        self.assertFalse(status)

        mock_exists.return_value = True
        mock_mktmp.return_value = "tmpfile"
        mock_untar.return_value = True
        structure = {'repositories': {'IMAGE': {'TAG': "tag", }, }, }
        mock_lstruct.return_value = structure
        mock_lrepo.return_value = ["R1", "R2", ]
        dlocapi = DockerLocalFileAPI(self.local)
        status = dlocapi.load("IMAGEFILE")
        self.assertEqual(status, ["R1", "R2", ])

    # def test_09__save_image(self):
    #     """Test09 DockerLocalFileAPI()._save_image()."""
    #     dlocapi = DockerLocalFileAPI(self.local)

    # def test_10_save(self):
    #     """Test10 DockerLocalFileAPI().save()."""
    #     dlocapi = DockerLocalFileAPI(self.local)






    ### NON existent methods, removed or moved to another class

    # @patch('udocker.container.localrepo.LocalRepository.set_version', autospec=True)
    # @patch('udocker.container.localrepo.LocalRepository.setup_tag', autospec=True)
    # @patch('udocker.container.localrepo.LocalRepository.cd_imagerepo', autospec=True)
    # @patch('udocker.container.localrepo.LocalRepository.sorted_layers', autospec=True)
    # @patch('udocker.container.localrepo.LocalRepository.find_top_layer_id', autospec=True)
    # @patch.object(DockerLocalFileAPI, '_copy_layer_to_repo')
    # def test_06__load_image(self, mock_copylayer, mock_findtop, mock_slayers, 
    #                         mock_cdimg, mock_settag, mock_setversion):
    #     """Test DockerLocalFileAPI()._load_image()."""
    #     mock_cdimg.return_value = True
    #     structure = {}
    #     dlocapi = DockerLocalFileAPI(self.local)
    #     status = dlocapi._load_image(structure, "IMAGE", "TAG")
    #     # self.assertFalse(status)

    #     mock_cdimg.return_value = False
    #     mock_settag.return_value = ""
    #     structure = {}
    #     dlocapi = DockerLocalFileAPI(self.local)
    #     status = dlocapi._load_image(structure, "IMAGE", "TAG")
    #     self.assertFalse(status)

    #     mock_cdimg.return_value = False
    #     mock_settag.return_value = "/dir"
    #     mock_setversion.return_value = False
    #     structure = {}
    #     dlocapi = DockerLocalFileAPI(self.local)
    #     status = dlocapi._load_image(structure, "IMAGE", "TAG")
    #     self.assertFalse(status)

    #     mock_cdimg.return_value = False
    #     mock_settag.return_value = "/dir"
    #     mock_setversion.return_value = True
    #     mock_findtop.return_value = "TLID"
    #     mock_slayers.return_value = []
    #     structure = {}
    #     dlocapi = DockerLocalFileAPI(self.local)
    #     status = dlocapi._load_image(structure, "IMAGE", "TAG")
    #     self.assertEqual(status, ['IMAGE:TAG'])

    #     mock_cdimg.return_value = False
    #     mock_settag.return_value = "/dir"
    #     mock_setversion.return_value = True
    #     mock_findtop.return_value = "TLID"
    #     mock_slayers.return_value = ["LID", ]
    #     mock_copylayer.return_value = False
    #     structure = {'layers': {'LID': {'VERSION': "1.0",
    #                                     'json_f': "f1",
    #                                     'layer_f': "f1", }, }, }
    #     dlocapi = DockerLocalFileAPI(self.local)
    #     status = dlocapi._load_image(structure, "IMAGE", "TAG")
    #     self.assertFalse(status)

    #     mock_cdimg.return_value = False
    #     mock_settag.return_value = "/dir"
    #     mock_setversion.return_value = True
    #     mock_findtop.return_value = "TLID"
    #     mock_slayers.return_value = ["LID", ]
    #     mock_copylayer.return_value = True
    #     structure = {'layers': {'LID': {'VERSION': "1.0",
    #                                     'json_f': "f1",
    #                                     'layer_f': "f1", }, }, }
    #     dlocapi = DockerLocalFileAPI(self.local)
    #     status = dlocapi._load_image(structure, "IMAGE", "TAG")
    #     self.assertEqual(status, ['IMAGE:TAG'])




    # @patch('udocker.docker.time.strftime')
    # @patch('udocker.docker.FileUtil.size')
    # def test_10_create_container_meta(self, mock_size, mock_stime):
    #     """Test DockerLocalFileAPI().create_container_meta()."""
    #     mock_size.return_value = 123
    #     mock_stime.return_value = "DATE"
    #     dlocapi = DockerLocalFileAPI(self.local)
    #     status = dlocapi.create_container_meta("LID")
    #     meta = {'comment': 'created by udocker',
    #             'created': 'DATE',
    #             'config': {'Env': None, 'Hostname': '', 'Entrypoint': None,
    #                        'PortSpecs': None, 'Memory': 0, 'OnBuild': None,
    #                        'OpenStdin': False, 'MacAddress': '', 'Cpuset': '',
    #                        'NetworkDisable': False, 'User': '',
    #                        'AttachStderr': False, 'AttachStdout': False,
    #                        'Cmd': None, 'StdinOnce': False, 'CpusShares': 0,
    #                        'WorkingDir': '', 'AttachStdin': False,
    #                        'Volumes': None, 'MemorySwap': 0, 'Tty': False,
    #                        'Domainname': '', 'Image': '', 'Labels': None,
    #                        'ExposedPorts': None},
    #             'container_config': {'Env': None, 'Hostname': '',
    #                                  'Entrypoint': None, 'PortSpecs': None,
    #                                  'Memory': 0, 'OnBuild': None,
    #                                  'OpenStdin': False, 'MacAddress': '',
    #                                  'Cpuset': '', 'NetworkDisable': False,
    #                                  'User': '', 'AttachStderr': False,
    #                                  'AttachStdout': False, 'Cmd': None,
    #                                  'StdinOnce': False, 'CpusShares': 0,
    #                                  'WorkingDir': '', 'AttachStdin': False,
    #                                  'Volumes': None, 'MemorySwap': 0,
    #                                  'Tty': False, 'Domainname': '',
    #                                  'Image': '', 'Labels': None,
    #                                  'ExposedPorts': None},
    #             'architecture': 'ARCH', 'os': 'OSVERSION',
    #             'id': 'LID', 'size': 123}
    #     self.assertEqual(status, meta)


if __name__ == '__main__':
    main()
