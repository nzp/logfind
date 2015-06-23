Prefind
========
A simple grep-like tool to find files containing one or more strings.  Prefind
[*]_ **find**\ s **P**\ ython **re**\ gular expressions in a **pre**\ defined
list of file paths (specified as Python regular expressions).

Usage
------
Prefind reads configuration from ``~/.prefind`` (by default) to figure out in
which files to look for the strings.  The format of this file is simple:

1. Each *absolute* file path on a line by itself.
2. Paths are specified as `Python regular expressions`_.
3. Blank lines (lines containing only white space characters) are ignored.
4. Lines beginning with ``#`` are comments and are also ignored.
5. Paths can have leading and trailing white space, which is stripped.

To use the program, run::

        prefind [-o] regex [regex ...]

String(s) to match are specified as `Python regular expressions`_ just like
file paths are.

The program has one significant option:

-o      Instead of the default regex chaining (logical ``AND``), use logical
        ``OR`` chaining.

The output is a list of file paths containing the specified regular
expression(s), each on a separate line.

If you get errors along the lines of ``UnicodeDecodeError``, invalid start
byte, etc. make sure your path regular expressions aren't hitting binary files
like gzipped log archives and so on.

Future
------
Planned are useful feature additions so that it actually has a point to exist,
an additional GUI of some kind, etc.

Development
-----------
To run tests do::

        python -m unittest discover

from the root of the distribution.


.. [*] Initially based on the idea `here`_.


.. _Python regular expressions: https://docs.python.org/2/howto/regex.html
.. _here: http://projectsthehardway.com/2015/06/16/project-1-logfind-2/
