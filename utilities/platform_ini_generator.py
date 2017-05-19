#!/usr/bin/env python3

# ungoogled-chromium-binaries: Concerns prebuilt versions of ungoogled-chromium
# Copyright (C) 2016  ungoogled-software contributors
#
# This file is part of ungoogled-chromium-binaries.
#
# ungoogled-chromium-binaries is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ungoogled-chromium-binaries is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ungoogled-chromium-binaries.  If not, see <http://www.gnu.org/licenses/>.

'''
This script takes in files and generates a platform ini as if they were uploaded to the Releases page

Output is to stdout, so consider redirecting the output to a file
'''

import sys
import pathlib
import hashlib
import collections

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
                hashes="\n".join(hashes_list)))
        return "\n\n".join(downloads_list)

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
        "Arguments: release_name github_user_or_organization_name github_project_name [file_name [file_name [...]]]",
        "",
        "This script outputs an INI file to standard output containing hashes and links to files from a GitHub Release.",
        "This script *cannot* be used to reference non-GitHub Release files.",
        "",
        "Argument descriptions:",
        "release_name is the name of the GitHub Release.",
        "github_user_or_organization_name and github_project_name specify the repository to use",
        "file_name are one or more paths to local files with the same name as the ones in the GitHub Release."
        ]), file=sys.stderr)

def main(args):
    print(args, file=sys.stderr)
    if args[0] == "--help" or args[0] == "-h" or args[0] == "help":
        print_usage_info()
        return 0
    args_parser = iter(args)
    current_version = next(args_parser)
    username = next(args_parser)
    project = next(args_parser)
    DownloadsManager.set_params(username, project, current_version)
    for filename in args_parser:
        DownloadsManager.add_download(pathlib.Path(filename))
    print(DownloadsManager.to_ini())
    return 0

if __name__ == "__main__":
    exit(main(sys.argv[1:]))
