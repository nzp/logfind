# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import os.path


def list_filepath_regexes():
    """Get the list of files to process.

    :rtype: list of strings (filepath regexes)

    """
    logfile_filepath = os.path.expanduser("~/.logfind")

    with open(logfile_filepath, "r") as f:
        filepath_regexes = [line.strip() for line in f]

    return filepath_regexes

