#!/usr/bin/env python3

# Copyright (c) 2017 The ungoogled-chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

'''
This script takes in files and generates a platform ini as if they were uploaded to the Releases page

Output is to stdout, so consider redirecting the output to a file
'''

import sys
import pathlib
import hashlib
import collections
import datetime

_REPOSITORY_NAME = 'ungoogled-chromium-binaries'

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
        return "https://github.com/{username}/{project}/releases/download/{version}/{filename}".format(
            filename=filename,
            version=cls._version,
            username=cls._username,
            project=cls._project)

    @classmethod
    def to_ini(cls):
        ini_header_template = '''[_metadata]
publication_time = {iso_timestamp}
github_author = {github_author}
# Add a `note` field here for additional information. Markdown is supported'''
        ini_header = ini_header_template.format(
            iso_timestamp=datetime.datetime.utcnow().isoformat(),
            github_author=cls._username
        )
        download_template = '''[{filename}]
url = {url}
{hashes}'''
        hash_template = '''{algorithm} = {filehash}'''

        downloads_list = list()
        for filename in sorted(cls._downloads):
            hashes_list = list()
            for algorithm in cls._downloads[filename]:
                hashes_list.append(hash_template.format(
                    algorithm=algorithm.lower(),
                    filehash=cls._downloads[filename][algorithm]))
            downloads_list.append(download_template.format(
                filename=filename,
                url=cls._create_download_url(filename),
                hashes="\n".join(sorted(hashes_list))
                )
            )
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

def print_usage_info():
    print("\n".join([
        "Arguments: release_name github_username file_path [file_path [...]]",
        "",
        "This script outputs an INI file to standard output containing hashes and links to files as if they were uploaded to a GitHub Release.",
        "The files that are passed in are read to generate hashes. Also, their file names are assumed to be identical in the GitHub Release.",
        "This script *cannot* be used to generate non-GitHub Release file URLs.",
        "",
        "Argument descriptions:",
        "release_name is the name of the GitHub Release.",
        "github_username is your username that contains the ungoogled-chromium-binaries fork.",
        "file_path are one or more paths to local files with the same name as the ones in the GitHub Release."
        ]), file=sys.stderr)

def main(args):
    print(args, file=sys.stderr)
    if args[0] == "--help" or args[0] == "-h" or args[0] == "help":
        print_usage_info()
        return 0
    args_parser = iter(args)
    current_version = next(args_parser)
    username = next(args_parser)
    DownloadsManager.set_params(username, _REPOSITORY_NAME, current_version)
    for filename in args_parser:
        DownloadsManager.add_download(pathlib.Path(filename))
    print(DownloadsManager.to_ini())
    return 0

if __name__ == "__main__":
    exit(main(sys.argv[1:]))
