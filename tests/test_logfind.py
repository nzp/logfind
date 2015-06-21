# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import unittest
import shutil
import os

from logfind import logfind


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
    fileout = "{}/.logfind".format(TEST_USER_HOME)

    def setUp(self):
        """Copy config file to `~/.logfind`."""

        shutil.copy(self.filein, self.fileout)

    def tearDown(self):
        """Remove the config file from `~/.logfind`."""

        os.remove(self.fileout)

    def test_list_filepath_regexes(self):
        """Test if `logfind.list_filepath_regexes` returns correctly."""

        inlist = logfind.list_filepath_regexes(TEST_USER_HOME)
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
        """Test if `logfind.get_paths` correctly finds RE paths."""

        # First member of the tuple is the RE, second is the list of paths
        # it matches.
        test_data = [
            ("{}/var/log/a.*\.log$".format(TEST_FILESYSTEM_ROOT), [
                "{}/var/log/apport.log".format(TEST_FILESYSTEM_ROOT),
                "{}/var/log/alternatives.log".format(TEST_FILESYSTEM_ROOT),
                "{}/var/log/auth.log".format(TEST_FILESYSTEM_ROOT),
                "{}/var/log/apt/term.log".format(TEST_FILESYSTEM_ROOT),
                "{}/var/log/apt/history.log".format(TEST_FILESYSTEM_ROOT),
                ]
            ),
            ("{}/var/log/Xorg\.\d+\.log$".format(TEST_FILESYSTEM_ROOT), [
                "{}/var/log/Xorg.0.log".format(TEST_FILESYSTEM_ROOT),
                "{}/var/log/Xorg.1.log".format(TEST_FILESYSTEM_ROOT),
                ]
            ),
            ("{}/var/log/m.*\.\d$".format(TEST_FILESYSTEM_ROOT), [
                "{}/var/log/mail.log.1".format(TEST_FILESYSTEM_ROOT),
                ]
            ),
        ]
        for case in test_data:
            out_paths = logfind.get_paths(case[0])
            self.assertEquals(case[1], out_paths)


class FinderTestCase(unittest.TestCase):
    """Test `logfind.finder()` finding strings in given files."""

    def test_finder_and(self):
        """Test searching ANDed regexes."""
        pass


if __name__ == "__main__":
    unittest.main()
