#!/usr/bin/env python3

# Copyright (c) 2019 The ungoogled-chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
'''
This script checks the platform INIs to ensure that the URLs are valid.

You will need to specify the INI files to check. There are certain methods to do this:

* Specify a CLI argument:
    * With "-", the standard input will be read for a newline-delimited list of files to read.
    * Specify a space-delimited list of paths to INI files to read.

    In both cases, non-INI files will be ignored.
* If no CLI argument is specified, then the tool will ask git via the CLI for a list of modified files in the working tree.
'''

import argparse
import os.path
import subprocess
import sys
from pathlib import Path

import requests

if __name__ == "__main__" and (__package__ is None or __package__ == ""):

    def _fix_relative_import():
        """Allow relative imports to work from anywhere"""
        parent_path = os.path.dirname(
            os.path.realpath(os.path.abspath(__file__)))
        sys.path.insert(0, os.path.dirname(parent_path))
        global __package__  #pylint: disable=global-variable-undefined
        __package__ = os.path.basename(parent_path)  #pylint: disable=redefined-builtin
        __import__(__package__)
        sys.path.pop(0)

    _fix_relative_import()

from . import _config_parsing


def get_ini_set(filelist_args):
    file_set = set()
    if not filelist_args:
        # Ask git for files in working tree
        # Get unstaged modified and untracked files
        file_set.update(
            subprocess.run(('git', 'ls-files', '--modified', '--others',
                            '--exclude-standard'),
                           capture_output=True,
                           check=True,
                           text=True).stdout.splitlines())
        # Get staged files
        file_set.update(
            subprocess.run(('git', 'diff', '--name-only', '--staged'),
                           capture_output=True,
                           check=True,
                           text=True).stdout.splitlines())
    elif filelist_args[0] == '-':
        # Read from stdin
        file_set.update(sys.stdin.read().strip().splitlines())
    else:
        # Assume list of files are provided
        file_set.update(filelist_args)
    # Include only .ini files
    return set(x for x in map(Path, file_set) if x.suffix.lower() == '.ini')


def verify_ini_files(inipath_iter):
    with requests.Session() as request_session:
        for inipath in inipath_iter:
            print('Checking', str(inipath))
            platform_version_files, _, _, _, _ = _config_parsing.parse_version_ini(
                inipath)
            for filename, filemeta in platform_version_files.items():
                fileurl, _ = filemeta
                response = request_session.get(
                    fileurl,
                    allow_redirects=True,
                    headers={'Range': 'bytes=0-1'})
                if not response.ok:
                    print(
                        f'ERROR: Got {response.status_code} ({response.reason}) for file: {filename}',
                        file=sys.stderr)
                    return 1
    return 0


def main(arg_list=None):
    """CLI interface"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'ini_path',
        nargs='*',
        help=
        ('Zero or more paths to platform INIs to check. '
         'If nothing is specified, then the git working tree will be checked. '
         'Specify "-" to read standard input.'))
    args = parser.parse_args(args=arg_list)
    inipath_set = get_ini_set(args.ini_path)
    if verify_ini_files(inipath_set):
        return 1
    if not inipath_set:
        print('Did not find any .ini files to check')
    return 0


if __name__ == "__main__":
    sys.exit(main())
