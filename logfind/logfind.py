# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import os
import re


def list_filepath_regexes(config_dir):
    """Get the list of files to process.

    The input is a file listing the file paths, specified as regular
    expressions, each on a line by itself.  Any whitespace around REs is
    stripped.  Blank lines are ignored.  Lines beginning with `#` are comments
    and are ignored.

    :param config_dir: directory in which to look for config file
    :type config_dir: string
    :rtype: list of strings (filepath regexes)

    """
    logfile_filepath = "{}/.logfind".format(config_dir)

    blank_line = re.compile(r"^\s+$")
    comment_line = re.compile(r"^#.*$")

    with open(logfile_filepath, "r") as f:
        filepath_regexes = [line.strip() for line in f
                if not (blank_line.match(line) or comment_line.match(line))]

    return filepath_regexes


def get_paths(regex, root="/"):
    """Find paths matching the regular expression.
    
    :param root: root directory for the walk
    :type root: string
    :param regex: regular expression to match against
    :rtype: list of strings (matched filepaths)
    """
    cre = re.compile(regex)
    path_list = []

    # To be able to have a reasonable (in fact, fast) walk time when starting
    # from "/" (or some other high root) we need to filter out unneeded
    # directories.  This would be easier if paths were shell globs, but they
    # are full REs.  Since `re` library doesn't understand filepaths, we have
    # to manually slice the whole regex, and then use intermediate directories
    # as regexes against which we filter at each level of the walk.
    #
    # Since string.split() gives "" as the first element of the list in this
    # case (because of the leading separator), we just discard it.
    re_parts = regex.split("/")
    del re_parts[0]

    for directory, children, filenames in os.walk(root):
        # When there is only 1 part left, we can't do any additional filtering.
        # Continuing to filter would clobber any directories matched by the last
        # part because re_parts would get = [], i.e. no directories would match
        # anymore.
        #
        # And until we get to one part, there's no point in trying to match
        # files, thus continue.
        if len(re_parts) > 1:
            children[:] = [child for child in children if re.match(re_parts[0], child)]
            re_parts[:] = re_parts[1:]
            continue

        for filename in filenames:
            path = os.path.join(directory, filename)
            if cre.match(path):
                path_list.append(path)

    return path_list

