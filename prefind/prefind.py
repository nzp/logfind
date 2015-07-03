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
    logfile_filepath = os.path.join(config_dir, ".prefind")

    blank_line = re.compile(r"^\s+$")
    comment_line = re.compile(r"^#.*$")

    with open(logfile_filepath, "r") as f:
        filepath_regexes = [line.strip() for line in f
                if not (blank_line.match(line) or comment_line.match(line))]

    return filepath_regexes


def get_paths(regex, root=os.sep):
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
    re_parts = regex.split(os.sep)
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


def finder(search_files, search_regexes, ored=False, case_insensitive=False):
    """Find given regexes in given files.

    :param search_files: files to search through
    :type search_files: list of strings (filepaths)
    :param search_regexes: regexes to search for
    :type search_regexes: list of strings (regexes)
    :param ored: are regexes to be ORed (default ANDed)
    :type ored: bool
    :param case_insensitive: should the search be case insensitive (default not)
    :type case_insensitive: bool
    :rtype: list of strings (filepaths that match)
    
    """
    if case_insensitive:
        regex_flags = re.MULTILINE|re.IGNORECASE
    else:
        regex_flags = re.MULTILINE

    compiled_regexes = [re.compile(r"{}".format(regex), flags=regex_flags)
                        for regex in search_regexes]
    matched_files = []

    def _read_files():
        for f in search_files:
            with open(f, "r") as infile:
                yield (infile.read(), f)

    # We don't need to know which regexes matched or not, so do short circuit
    # evaluation.
    for text, path in _read_files():
        if ored:
            for r in compiled_regexes:
                if r.search(text):
                    matched_files.append(path)
                    break
        else:
            matched_files.append(path)
            for r in compiled_regexes:
                if not r.search(text):
                    matched_files.remove(path)
                    break

    return matched_files

