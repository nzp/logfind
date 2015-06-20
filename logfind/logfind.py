# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import os
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


def get_paths(regex, root="/var/log"):
    """Find paths matching the regular expression.
    
    :param root: root directory for the walk
    :type root: string
    :param regex: regular expression to match against
    :rtype: list of strings (matched filepaths)
    """
    cre = re.compile(regex)
    path_list = []

    # TODO: This needs to do more work to filter parent directories.  Since
    # the search in reality needs to start at / it would take an unacceptable
    # amount of time to finish if it just walked the filesystem naively from
    # top to bottom.
    for directory, children, filenames in os.walk(root):
        for filename in filenames:
            path = os.path.join(directory, filename)

            if cre.match(path):
                path_list.append(path)
    
    return path_list
