#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess


def main():
    # Get current SHA
    head_sha = os.environ['CIRRUS_CHANGE_IN_REPO']

    # Get base SHA
    # Set default to one commit before
    base_sha = head_sha + '^'
    for candidate_env in ('CIRRUS_LAST_GREEN_CHANGE', 'CIRRUS_BASE_SHA'):
        candidate_sha = os.getenv(candidate_env)
        if candidate_sha:
            base_sha = candidate_sha
            break

    # Get file list via git
    print(
        subprocess.run(('git', 'diff', '--name-only', f'{base_sha}..{head_sha}'),
                       check=True,
                       capture_output=True,
                       text=True).stdout.strip())


if __name__ == '__main__':
    main()
