import os
import re
from concurrent import futures


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
    :rtype: set of strings (matched filepaths)

    """
    cre = re.compile(regex)

    # To make sure there are no duplicate paths, use a set.
    path_set = set()

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
                path_set.add(path)

    return path_set


class _search_file:
    # Since file searching callable needs to be pickable to work with
    # concurrent.future module's map() in finder(), it can't be a closure
    # (which we need to wrap the value of ored) so __call__ gives equivalent
    # functionality.  That is why this is a class in the first place.
    def __init__(self, ored, regexes):
        self.ored = ored
        self.regexes = regexes

    def __call__(self, file_to_search):
        with open(file_to_search, "r") as f:
            text = f.read()

        if self.ored:
            for r in self.regexes:
                if r.search(text):
                    return file_to_search
        else:
            matched = True
            for r in self.regexes:
                if not r.search(text):
                    matched = False
                    break

            if matched:
                return file_to_search


def finder(search_files, search_regexes, ored=False, case_insensitive=False):
    """Find given regexes in given files.

    :param search_files: files to search through
    :type search_files: an iterable of strings (filepaths)
    :param search_regexes: regexes to search for
    :type search_regexes: list of strings (regexes)
    :param ored: are regexes to be ORed (default ANDed)
    :type ored: bool
    :param case_insensitive: should the search be case insensitive (default not)
    :type case_insensitive: bool
    :rtype: set of strings (filepaths that match)
    
    """
    if case_insensitive:
        regex_flags = re.MULTILINE|re.IGNORECASE
    else:
        regex_flags = re.MULTILINE

    compiled_regexes = [re.compile(r"{}".format(regex), flags=regex_flags)
                        for regex in search_regexes]

    with futures.ProcessPoolExecutor() as executor:
        searcher = _search_file(ored, compiled_regexes)
        matched_files = {f for f in executor.map(searcher, search_files) if f}

    return matched_files

