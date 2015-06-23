# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import unittest
import shutil
import os

from prefind import prefind


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

FIXTURES_DIR = "{}/fixtures".format(BASE_DIR)
FIXTURES_LOG_DIR = "{}/logs".format(FIXTURES_DIR)

TEST_FILESYSTEM_ROOT = "{}/test_root".format(BASE_DIR)
TEST_USER_HOME = "{}/home/test".format(TEST_FILESYSTEM_ROOT)
TEST_LOG_DIR = "{}/var/log".format(TEST_FILESYSTEM_ROOT)


def setUpModule():
    """Set up testing environment."""
    if os.path.exists(TEST_FILESYSTEM_ROOT):
        shutil.rmtree(TEST_FILESYSTEM_ROOT)

    os.makedirs(TEST_USER_HOME)
    shutil.copytree(FIXTURES_LOG_DIR, TEST_LOG_DIR)


def tearDownModule():
    """Clean the testing environment."""
    shutil.rmtree(TEST_FILESYSTEM_ROOT)


class ConfigFileReadTestCase(unittest.TestCase):
    """Test config file reading."""

    filein = "{}/logfile".format(FIXTURES_DIR)
    fileout = "{}/.prefind".format(TEST_USER_HOME)

    def setUp(self):
        """Copy config file to `~/.prefind`."""

        shutil.copy(self.filein, self.fileout)

    def tearDown(self):
        """Remove the config file from `~/.prefind`."""

        os.remove(self.fileout)

    def test_list_filepath_regexes(self):
        """Test if `prefind.list_filepath_regexes` returns correctly."""

        inlist = prefind.list_filepath_regexes(TEST_USER_HOME)
        outlist = [
                "/usr/share/log/blarhf",
                "/usr/.*/.*",
                "/[a-zA-Z0-9]+/.+",
                "~/.logs/.*",
                ]

        self.assertEqual(inlist, outlist)


class FindFilesTestCase(unittest.TestCase):
    """Test log file discovery."""

    def test_get_paths(self):
        """Test if `prefind.get_paths` correctly finds RE paths."""

        # First member of the tuple is the RE, second is the list of paths
        # it matches.
        test_data = [
            ("{}/a.*\.log$".format(TEST_LOG_DIR), [
                "{}/apport.log".format(TEST_LOG_DIR),
                "{}/alternatives.log".format(TEST_LOG_DIR),
                "{}/auth.log".format(TEST_LOG_DIR),
                "{}/apt/term.log".format(TEST_LOG_DIR),
                "{}/apt/history.log".format(TEST_LOG_DIR),
                ]
            ),
            ("{}/Xorg\.\d+\.log$".format(TEST_LOG_DIR), [
                "{}/Xorg.0.log".format(TEST_LOG_DIR),
                "{}/Xorg.1.log".format(TEST_LOG_DIR),
                ]
            ),
            ("{}/m.*\.\d$".format(TEST_LOG_DIR), [
                "{}/mail.log.1".format(TEST_LOG_DIR),
                ]
            ),
        ]
        for case in test_data:
            out_paths = prefind.get_paths(case[0])
            self.assertEquals(case[1], out_paths)


class FinderTestCase(unittest.TestCase):
    """Test `prefind.finder()` finding strings in given files."""

    search_files = [
            "{}/testlog.1".format(TEST_LOG_DIR),
            "{}/testlog.2".format(TEST_LOG_DIR),
            "{}/testlog.3".format(TEST_LOG_DIR),
            ]

    def test_finder_and(self):
        """Test searching ANDed regexes."""

        search_regexes = [
                "one",  # missing in testlog.3
                "two",
                "three",
                "Ge.+\sWhee.*:.*$",
                ]
        test_result = [
                "{}/testlog.1".format(TEST_LOG_DIR),
                "{}/testlog.2".format(TEST_LOG_DIR),
                ]
        result = prefind.finder(self.search_files, search_regexes)

        self.assertEqual(test_result, result)

    def test_finder_or(self):
        """Test searching ORed regexes."""

        search_regexes = [
                "klapna",  # in neither file.
                "lugubrious",  # in testlog.3
                "craptastic",  # in testlog.3
                "3Ge.+\sWhee.*:.*$",  # in testlog.2
                ]
        test_result = [
                "{}/testlog.2".format(TEST_LOG_DIR),
                "{}/testlog.3".format(TEST_LOG_DIR),
                ]
        result = prefind.finder(self.search_files, search_regexes, anded=False)

        self.assertEqual(test_result, result)


if __name__ == "__main__":
    unittest.main()
