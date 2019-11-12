#!/usr/bin/env python3

# Copyright (c) 2017 The ungoogled-chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
'''
Tool to generate a platform .ini as if it were uploaded to GitHub Releases
'''

import argparse
import collections
import datetime
import hashlib
import os.path
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__" and (__package__ is None or __package__ == ""):

    def _fix_relative_import():
        """Allow relative imports to work from anywhere"""
        parent_path = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
        sys.path.insert(0, os.path.dirname(parent_path))
        global __package__ #pylint: disable=global-variable-undefined
        __package__ = os.path.basename(parent_path) #pylint: disable=redefined-builtin
        __import__(__package__)
        sys.path.pop(0)

    _fix_relative_import()

from . import check_platform_ini

_REPOSITORY_NAME = 'ungoogled-chromium-binaries'
_CONFIG_ROOT = Path(__file__).resolve().parent.parent / 'config' / 'platforms'

# GitHub Releases automatically replaces some characters
_URL_REPLACEMENTS = {
    '~': '.',
}


class DownloadsManager:
    _algorithms = ["md5", "sha1", "sha256"]
    _downloads = dict()
    _username = None
    _project = None
    _version = None

    @classmethod
    def set_params(cls, username, project, version):
        cls._username = username
        cls._project = project
        cls._version = version

    @classmethod
    def _create_download_url(cls, filename):
        url = "https://github.com/{username}/{project}/releases/download/{version}/{filename}".format(
            filename=filename, version=cls._version, username=cls._username, project=cls._project)
        for initial, replacement in _URL_REPLACEMENTS.items():
            url = url.replace(initial, replacement)
        return url

    @classmethod
    def to_ini(cls):
        ini_header_template = '''[_metadata]
status = development
publication_time = {iso_timestamp}
github_author = {github_author}
# Add a `note` field here for additional information. Markdown is supported'''
        ini_header = ini_header_template.format(
            iso_timestamp=datetime.datetime.utcnow().isoformat(), github_author=cls._username)
        download_template = '''[{filename}]
url = {url}
{hashes}'''
        hash_template = '''{algorithm} = {filehash}'''

        downloads_list = list()
        for filename in sorted(cls._downloads):
            hashes_list = list()
            for algorithm in cls._downloads[filename]:
                hashes_list.append(
                    hash_template.format(
                        algorithm=algorithm.lower(), filehash=cls._downloads[filename][algorithm]))
            downloads_list.append(
                download_template.format(
                    filename=filename,
                    url=cls._create_download_url(filename),
                    hashes="\n".join(sorted(hashes_list))))
        return ini_header + '\n\n' + '\n\n'.join(downloads_list)

    @classmethod
    def add_download(self, filepath):
        if filepath.name in self._downloads:
            raise Exception("File {!s} already added".format(filepath))
        self._downloads[filepath.name] = dict()
        with filepath.open("rb") as fileobj:
            for algorithm in self._algorithms:
                hasher = hashlib.new(algorithm)
                hasher.update(fileobj.read())
                self._downloads[filepath.name][algorithm] = hasher.hexdigest()
                fileobj.seek(0)


def _get_tag_name(args):
    if args.tag:
        return args.tag
    else:
        return subprocess.run(['git', 'describe', '--abbrev=0', '--tags'],
                              check=True,
                              capture_output=True,
                              text=True,
                              cwd=args.git).stdout.strip()


def _get_platform_name(output_path):
    current_path = output_path.resolve()
    names = list()
    while current_path != _CONFIG_ROOT:
        names.append((current_path / 'display_name').read_text().strip())
        current_path = current_path.parent
    names.reverse()
    return ' '.join(names)


def _is_path_inside(inner, outer):
    return outer.parts == inner.parts[:len(outer.parts)]


def main(arg_list=None):
    """
    This script outputs an INI file to standard output containing hashes and links to files as if they were uploaded to a GitHub Release.
    The files that are passed in are read to generate hashes. Also, their file names are assumed to be identical in the GitHub Release.
    This script *cannot* be used to generate non-GitHub Release file URLs.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        '--output', '-o', type=Path, required=True, help='Directory to write .ini files to')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--tag', '-t', help='Name of the tag used in the GitHub Release')
    group.add_argument(
        '--git',
        '-g',
        type=Path,
        help='Path to the git repo to get the latest tag (of the current branch)')
    parser.add_argument(
        '--username',
        '-u',
        required=True,
        help='GitHub username containing the fork of ungoogled-chromium-binaries')
    parser.add_argument(
        '--skip-commit',
        action='store_true',
        help='Skip creating a git commit automatically with the .ini file')
    parser.add_argument(
        '--skip-checks',
        action='store_true',
        help='Skip validation of the URLs for the new platform .ini')
    parser.add_argument(
        '--project',
        '-p',
        default=_REPOSITORY_NAME,
        help='GitHub project containing the Release (Default: %(default)s)')
    parser.add_argument(
        'file_path',
        nargs='+',
        help=('One or more paths to local files with the same name as the ones '
              'in the GitHub Release. Used for URL and hash generation in the INI.'))
    args = parser.parse_args(args=arg_list)

    # Check script preconditions and set required variables
    if not _is_path_inside(args.output.resolve(),
                           _CONFIG_ROOT) and not len(args.output.parts) > len(_CONFIG_ROOT.parts):
        parser.error('Directory for .ini must be inside config/platforms/PLATFORM_HERE')
    tag_name = _get_tag_name(args)
    ini_path = args.output / f'{tag_name}.ini'
    if not ini_path.parent.exists():
        parser.error('Parent directory for output .ini does not exist. '
                     'Please create it and add display_name at each level.')
    if not args.skip_commit:
        # Abort early if files are staged, since we can't commit only the .ini
        if subprocess.run(['git', 'diff', '--staged', '--quiet', '--exit-code']).returncode != 0:
            parser.error('You have staged changes in your git working tree. '
                         'Please clear the staging area (commit or stash), or use --skip-commit')

    # Actual work
    DownloadsManager.set_params(args.username, args.project, tag_name)
    for filename in args.file_path:
        DownloadsManager.add_download(Path(filename))
    ini_path.write_text(DownloadsManager.to_ini())

    # Postconditions and finalizing
    if not args.skip_checks:
        if check_platform_ini.verify_ini_files((ini_path, )):
            print(
                'ERROR: Validation of new .ini failed. '
                'Check that your release is published and your arguments are correct.',
                file=sys.stderr)
            return 1
    if not args.skip_commit:
        subprocess.run(['git', 'add', str(ini_path)], check=True)
        subprocess.run(
            ['git', 'commit', '-m', f'Add {tag_name} for {_get_platform_name(args.output)}'],
            check=True)
        print('INFO: Commit successful. Make sure to push your commit.')
    return 0


if __name__ == "__main__":
    sys.exit(main())
