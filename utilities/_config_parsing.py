# Utilities for parsing files under config/

import configparser
import datetime


def parse_version_ini(ini_path):
    """Parse a version INI file"""
    files = dict()
    publication_time = None
    github_author = None
    install_info = None
    note = '*(none)*'

    version_config = configparser.ConfigParser()
    version_config.read(str(ini_path))
    for section in version_config:
        if section == "DEFAULT":
            continue
        elif section.lower() == "_metadata":
            for config_attribute in version_config[section]:
                if config_attribute.lower() == "publication_time":
                    publication_time = datetime.datetime.strptime(
                        version_config[section][config_attribute],
                        "%Y-%m-%dT%H:%M:%S.%f").replace(
                            tzinfo=datetime.timezone.utc)
                elif config_attribute.lower() == "github_author":
                    github_author = version_config[section][config_attribute]
                elif config_attribute.lower() == "install_info":
                    install_info = version_config[section][
                        config_attribute].strip()
                elif config_attribute.lower() == "note":
                    note = version_config[section][config_attribute]
                elif config_attribute.lower() == "status":
                    # Statuses are deprecated
                    pass
                else:
                    raise ValueError("Unknown _metadata attribute '{}'".format(
                        config_attribute))
        else:
            file_hashes = dict()
            url = None
            for attribute_key in version_config[section]:
                if attribute_key.lower() == "url":
                    url = version_config[section][attribute_key]
                else:
                    file_hashes[attribute_key.upper(
                    )] = version_config[section][attribute_key]
            if url is None:
                raise ValueError("url is None. Section: {}, Path: {}".format(
                    section, str(ini_path)))
            files[section] = (url, file_hashes)
    return files, publication_time, github_author, install_info, note
