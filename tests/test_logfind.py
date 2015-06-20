# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import unittest
import shutil
import os

from logfind import logfind


class LogfindFileReadTestCase(unittest.TestCase):
    """Test logfind file reading."""

    filein = "{}/logfile".format(
        os.path.abspath(os.path.dirname(__file__)))

    fileout = os.path.expanduser("~/.logfind")

    def setUp(self):
        """Copy logfind file to `~/.logfind`."""

        shutil.copy(self.filein, self.fileout)

    def tearDown(self):
        """Remove the logfind file from `~/.logfind`."""
        
        os.remove(self.fileout)

    def test_list_filepath_regexes(self):
        """Test if `logfind.list_filepaths` returns correctly."""

        inlist = logfind.list_filepath_regexes()
        outlist = [
                "/usr/share/log/blarhf",
                "/usr/.*/.*",
                "/[a-zA-Z0-9]+/.+",
                "~/.logs/.*",
                ]

        self.assertEqual(inlist, outlist)


if __name__ == "__main__":
    unittest.main()
