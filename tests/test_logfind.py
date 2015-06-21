# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import unittest
import shutil
import os

from logfind import logfind


# XXX: All of the fixture data needs to be made self contained.  Now it just
# uses concrete files on my own local filesystem, which is dumb.

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
        """Test if `logfind.list_filepath_regexes` returns correctly."""

        inlist = logfind.list_filepath_regexes()
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
                ("/var/log/a.*\.log$",
                    [
                        "/var/log/apport.log",
                        "/var/log/alternatives.log",
                        "/var/log/auth.log",
                        "/var/log/apt/term.log",
                        "/var/log/apt/history.log",
                        ]
                ),
                ("/var/log/Xorg\.\d+\.log$",
                    [
                        "/var/log/Xorg.0.log",
                        "/var/log/Xorg.1.log",
                        ]
                ),
                ("/var/log/m.*\.\d$",
                    [
                        "/var/log/mail.log.1",
                        ]
                )
            ]
        for case in test_data:
            out_paths = logfind.get_paths(case[0])
            self.assertEquals(case[1], out_paths)


if __name__ == "__main__":
    unittest.main()
