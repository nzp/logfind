import unittest
import shutil
import os

from prefind import prefind


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures")
FIXTURES_LOG_DIR = os.path.join(FIXTURES_DIR, "logs")

TEST_FILESYSTEM_ROOT = os.path.join(BASE_DIR, "test_root")
TEST_USER_HOME = os.path.join(TEST_FILESYSTEM_ROOT, "home", "test")
TEST_LOG_DIR = os.path.join(TEST_FILESYSTEM_ROOT, "var", "log")


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

    filein = os.path.join(FIXTURES_DIR, "logfile")
    fileout = os.path.join(TEST_USER_HOME, ".prefind")

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
                # No need for os.path on paths, these are just strings in the
                # test file.
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
            (os.path.join(TEST_LOG_DIR, r"a.*\.log$"), [
                os.path.join(TEST_LOG_DIR, "apport.log"),
                os.path.join(TEST_LOG_DIR, "alternatives.log"),
                os.path.join(TEST_LOG_DIR, "auth.log"),
                os.path.join(TEST_LOG_DIR, "apt", "term.log"),
                os.path.join(TEST_LOG_DIR, "apt", "history.log"),
                ]
            ),
            (os.path.join(TEST_LOG_DIR, r"Xorg\.\d+\.log$"), [
                os.path.join(TEST_LOG_DIR, "Xorg.0.log"),
                os.path.join(TEST_LOG_DIR, "Xorg.1.log"),
                ]
            ),
            (os.path.join(TEST_LOG_DIR, r"m.*\.\d$"), [
                os.path.join(TEST_LOG_DIR, "mail.log.1"),
                ]
            ),
        ]
        for case in test_data:
            out_paths = prefind.get_paths(case[0])
            self.assertEqual(case[1], out_paths)


class FinderTestCase(unittest.TestCase):
    """Test `prefind.finder()` finding strings in given files."""

    search_files = [
            os.path.join(TEST_LOG_DIR, "testlog.1"),
            os.path.join(TEST_LOG_DIR, "testlog.2"),
            os.path.join(TEST_LOG_DIR, "testlog.3"),
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
                os.path.join(TEST_LOG_DIR, "testlog.1"),
                os.path.join(TEST_LOG_DIR, "testlog.2"),
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
                os.path.join(TEST_LOG_DIR, "testlog.2"),
                os.path.join(TEST_LOG_DIR, "testlog.3"),
                ]
        result = prefind.finder(self.search_files, search_regexes, anded=False)

        self.assertEqual(test_result, result)


if __name__ == "__main__":
    unittest.main()
