# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import os.path
import re


def list_filepath_regexes():
    """Get the list of files to process.

    The input is a file listing the file paths, specified as regular
    expressions, each on a line by itself.  Any whitespace around REs is
    stripped.  Blank lines are ignored.  Lines beginning with `#` are comments
    and are ignored.

    :rtype: list of strings (filepath regexes)

    """
    logfile_filepath = os.path.expanduser("~/.logfind")

    blank_line = re.compile(r"^\s+$")
    comment_line = re.compile(r"^#.*$")

    with open(logfile_filepath, "r") as f:
        filepath_regexes = [line.strip() for line in f
                if not (blank_line.match(line) or comment_line.match(line))]

    return filepath_regexes

