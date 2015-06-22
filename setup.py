#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup

config = {
        "name": "Logfind",
        "description": (
            "A simple grep-like tool to find files containing given string(s)."),
        "version": "0.1",
        "author": "Nikola Pavlović",
        "author_email": "npavlovi@gmail.com",
        "url": "https://github.com/nzp/logfind",
        "packages": ["logfind"],
        "license": "BSD 2-Clause",
        "scripts": ["bin/logfind"],
        "data_files": [
            ("docs", [
                "README.rst",
                "LICENSE",
                ])]
        }

setup(**config)
