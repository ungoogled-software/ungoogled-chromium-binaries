#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

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
Generates the website files
'''

import pathlib
import configparser
import string
import re
import shutil

_CONFIG = pathlib.Path("config")
_PAGE_TEMPLATES = _CONFIG / pathlib.Path("page_templates")
_OUTPUT_SUFFIX = ".md"
_INDEX_FRONTPAGE = _PAGE_TEMPLATES / pathlib.Path("index_frontpage" + _OUTPUT_SUFFIX + ".in")
_INDEX_DIRECTORY = _PAGE_TEMPLATES / pathlib.Path("index_directory" + _OUTPUT_SUFFIX + ".in")
_OUTPUT_INDEX = pathlib.Path("index" + _OUTPUT_SUFFIX)
_VERSION_INPUT = _PAGE_TEMPLATES / pathlib.Path("version" + _OUTPUT_SUFFIX + ".in")
_PLATFORMS = _CONFIG / pathlib.Path("platforms")
_VALID_VERSIONS = _CONFIG / pathlib.Path("valid_versions")
_RELEASES = pathlib.Path("releases")
_DISPLAY_NAME = pathlib.Path("display_name")

# For printing out info and Markdown
_INDENTATION = "    "

_valid_versions = list()

class PageFileStringTemplate(string.Template):
    '''
    Custom string substitution class

    Inspired by
    http://stackoverflow.com/questions/12768107/string-substitutions-using-templates-in-python
    '''

    pattern = r"""
    {delim}(?:
      (?P<escaped>{delim}) |
      _(?P<named>{id})      |
      {{(?P<braced>{id})}}   |
      (?P<invalid>{delim}((?!_)|(?!{{)))
    )
    """.format(delim=re.escape("$ungoog"), id=string.Template.idpattern)

class PlatformVersion:
    def __init__(self, config_path, parent):
        if not config_path.is_file():
            raise FileNotFoundError(str(config_path))
        self._real_path = config_path
        self.path = self._real_path.relative_to(_PLATFORMS).parent / self._real_path.stem
        self.parent = parent
        self.version = self.path.name
        self.display_name = self.version
        if not self.version in _valid_versions:
            raise ValueError("{} is not a valid version. Directory: {}".format(self.version, str(self.path.parent)))
        self.files = dict()
        self.note = None

        version_config = configparser.ConfigParser()
        version_config.read(str(self._real_path))
        for section in version_config:
            if section == "DEFAULT":
                continue
            elif section.lower() == "config":
                for config_attribute in version_config[section]:
                    if config_attribute.lower() == "note":
                        self.note = version_config[section][config_attribute]
            else:
                file_hashes = dict()
                url = None
                for attribute_key in version_config[section]:
                    if attribute_key.lower() == "url":
                        url = version_config[section][attribute_key]
                    else:
                        file_hashes[attribute_key.upper()] = version_config[section][attribute_key]
                if url is None:
                    raise ValueError("url is None. Section: {}, Path: {}".format(section, str(self.path)))
                self.files[section] = (url, file_hashes)

    def __lt__(self, other):
        return self.version < other.version

    def __str__(self):
        return "A Version: {}".format(str(self.version))

    def __repr__(self):
        return str(self)

class PlatformDirectory:
    def __init__(self, dir_path, parent):
        if not dir_path.is_dir():
            raise NotADirectoryError(str(dir_path))
        self._real_path = dir_path
        self.path = self._real_path.relative_to(_PLATFORMS)
        self.parent = parent
        self.children = list()
        self.versions = list()

        with (dir_path / _DISPLAY_NAME).open() as display_name_file:
            self.display_name = display_name_file.read().splitlines()[0]

        for config_path in sorted(self._real_path.glob("*.ini"), reverse=True):
            self.versions.append(PlatformVersion(config_path, self))

    def __lt__(self, other):
        return self.path < other.path

    def recursively_read_children(self):
        for entry in self._real_path.iterdir():
            if entry.is_dir():
                tmp_dir = PlatformDirectory(entry, self)
                tmp_dir.recursively_read_children()
                self.children.append(tmp_dir)
        self.children.sort()

    def __str__(self):
        return "Directory: {}".format(str(self.path))

    def __repr__(self):
        return str(self)

def read_valid_versions():
    with _VALID_VERSIONS.open() as valid_versions_file:
        for line in valid_versions_file.read().splitlines():
            if len(line) > 0 and not line.startswith("#"):
                _valid_versions.append(line)
    _valid_versions.sort()

def read_config():
    root_dir = PlatformDirectory(_PLATFORMS, None)
    root_dir.name = _RELEASES.name
    root_dir.recursively_read_children()
    return root_dir

def preorder_traversal(root_dir, include_versions=False):
    stack = list()
    stack.append(root_dir)
    while len(stack) > 0:
        directory = stack.pop()
        yield directory
        if include_versions:
            for version in directory.versions:
                yield version
        for child in sorted(directory.children, reverse=True):
            stack.append(child)

def print_config(root_dir):
    for node in preorder_traversal(root_dir, include_versions=True):
        for i in range(len(node.path.parts)):
            print(_INDENTATION, end="")
        print(node.display_name, end="")
        if isinstance(node, PlatformDirectory):
            print()
        elif isinstance(node, PlatformVersion):
            indentation_amt = len(node.path.parts)
            if node.note:
                print(" (HAS NOTE)")
            else:
                print()
            for filename in sorted(node.files):
                for i in range(indentation_amt + 1):
                    print(_INDENTATION, end="")
                print(filename)
        else:
            print("Unknown node ", node)

def _get_node_weburl(node):
    # Hacky
    return "/" + _RELEASES.name + "/" + "/".join(node.path.parts)

def _write_frontpage_index(root_dir):
    target_path = _OUTPUT_INDEX

    download_markdown = str()

    for node in preorder_traversal(root_dir):
        if node == root_dir:
            continue
        for i in range(len(node.path.parts) - 1):
            download_markdown += _INDENTATION
        download_markdown += "* [{}]({})".format(node.display_name, _get_node_weburl(node))
        if len(node.versions) > 0:
            download_markdown += ": [{}]({})".format(node.versions[0].version, _get_node_weburl(node.versions[0]))
        download_markdown += "\n"

    page_subs = dict(
        latest_downloads=download_markdown
    )
    with _INDEX_FRONTPAGE.open() as input_file:
        content = PageFileStringTemplate(input_file.read()).substitute(**page_subs)
    with target_path.open("w") as output_file:
        output_file.write(content)

def _write_directory_index(directory_node):
    target_path = _RELEASES / directory_node.path / _OUTPUT_INDEX

    markdown_urls = list()
    current_node = directory_node
    while not current_node is None:
        markdown_urls.insert(0, "[{}]({})".format(current_node.display_name, _get_node_weburl(current_node)))
        current_node = current_node.parent

    versions_list_markdown = str()
    if len(directory_node.versions) > 0:
        versions_list_markdown = "## Available versions\n\n"
        for version in directory_node.versions:
            versions_list_markdown += "* [{}]({})\n".format(version.version, _get_node_weburl(version))

    directory_list_markdown = str()
    if len(directory_node.children) > 0:
        directory_list_markdown = "## Subgroupings\n\n"
        for subdirectory in directory_node.children:
            directory_list_markdown += "* [{}]({})\n".format(subdirectory.display_name, _get_node_weburl(subdirectory))

    page_subs = dict(
        current_path=" / ".join(markdown_urls),
        versions_list=versions_list_markdown,
        directory_list=directory_list_markdown
    )
    with _INDEX_DIRECTORY.open() as input_file:
        content = PageFileStringTemplate(input_file.read()).substitute(**page_subs)
    with target_path.open("w") as output_file:
        output_file.write(content)

def _write_version_page(version_node):
    target_path = _RELEASES / version_node.path.parent / (version_node.version + _OUTPUT_SUFFIX)

    display_names = list()
    current_node = version_node.parent
    while not current_node.parent is None:
        display_names.insert(0, current_node.display_name)
        current_node = current_node.parent

    markdown_urls = list()
    current_node = version_node
    while not current_node is None:
        markdown_urls.insert(0, "[{}]({})".format(current_node.display_name, _get_node_weburl(current_node)))
        current_node = current_node.parent

    if not version_node.note is None:
        note_markdown = version_node.note
    else:
        note_markdown = str()

    download_list_markdown = str()
    for filename in sorted(version_node.files.keys()):
        url, hashes = version_node.files[filename]
        download_list_markdown += "* [{}]({})\n".format(filename, url)
        for hashname in sorted(hashes.keys()):
            download_list_markdown += _INDENTATION + "* {}: `{}`\n".format(hashname, hashes[hashname])

    page_subs = dict(
        version=version_node.version,
        display_name=" - ".join(display_names),
        current_path=" / ".join(markdown_urls),
        note=note_markdown,
        download_list=download_list_markdown
    )
    with _VERSION_INPUT.open() as input_file:
        content = PageFileStringTemplate(input_file.read()).substitute(**page_subs)
    with target_path.open("w") as output_file:
        output_file.write(content)

def write_website(root_dir):
    if _RELEASES.exists():
        if not _RELEASES.is_dir():
            raise NotADirectoryError("The releases directory is not a directory")
        shutil.rmtree(str(_RELEASES))

    for node in preorder_traversal(root_dir, include_versions=True):
        if isinstance(node, PlatformDirectory):
            (_RELEASES / node.path).mkdir()
            _write_directory_index(node)
        elif isinstance(node, PlatformVersion):
            _write_version_page(node)
        else:
            print("Unknown node ", node)

    _write_frontpage_index(root_dir)

if __name__ == "__main__":
    read_valid_versions()

    root_dir = read_config()

    print_config(root_dir)
    write_website(root_dir)
