#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys


def _log(msg):
    print(msg, file=sys.stderr)


def _run_subprocess(cmd_line, check=False):
    """Wrapper around subprocess.run that logs results on failure instead of aborting"""
    result = subprocess.run(
        cmd_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode:
        _log(
            f"ERROR: Command '{cmd_line}' returned non-zero exit status {result.returncode}"
        )
        _log(f"===BEGIN STDOUT===\n{result.stdout}\n===END STDOUT===")
        _log(f"===BEGIN STDERR===\n{result.stderr}\n===END STDERR===")
        if check:
            sys.exit(result.returncode)
    return result


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

    # Log some info to diagnose possible CI bugs
    _log(f'Found base hash {base_sha} and current hash {head_sha}')

    get_diff_filelist = lambda: _run_subprocess(('git', 'diff', '--name-only', '--diff-filter=ACMR', f'{base_sha}..{head_sha}'))

    # Get file list via git
    result = get_diff_filelist()
    if result.returncode:
        # It might have failed because the PR base is not HEAD of base repo
        # Therefore, we try to rebase against master and try again
        # Note that this doesn't have to be a PR, in case Cirrus CI clones a repo that does not reflect
        # the environment variables
        clone_url = os.environ['CIRRUS_REPO_CLONE_URL']
        _log(
            f"'git diff' failed; trying to rebase against current HEAD of base repo ({clone_url})..."
        )
        _run_subprocess(('git', 'pull', '--rebase', clone_url, base_sha),
                        check=True)
        result = get_diff_filelist()

    # "result" may be re-assigned before we reach here
    if result.returncode:
        sys.exit(result.returncode)
    print(result.stdout.strip())


if __name__ == '__main__':
    main()
