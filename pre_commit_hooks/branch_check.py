from __future__ import annotations

import argparse
import sys
import subprocess
import re
import os

# Default patterns are for conventional branches. See:
# https://conventional-branch.github.io/
DEFAULT_ALLOWED_PATTERNS = [
    '^(feature|bugfix|hotfix|release|chore)/[a-z0-9/.-]*[a-z0-9]$',
    '^(main|master|develop)$'
]
DEFAULT_DENIED_PATTERNS = []

def get_forge_branch() -> str:
    """
    Get the current branch name from CI environment variables. This function
    checks for known environment variables set at software forges in their CI
    systems. Focus is on the source branch of merge/pull requests as git will
    often be in detached mode in that case.

    Returns:
        The current branch name as a string, empty when not found
    """

    # List of known CI environment variables for branch name
    ci_branch_env_vars = [
        'GITHUB_HEAD_REF',                      # GitHub Actions
        'CI_MERGE_REQUEST_SOURCE_BRANCH_NAME',  # GitLab CI
        'BITBUCKET_BRANCH',                     # Bitbucket Pipelines
    ]
    for env_var in ci_branch_env_vars:
        branch_name = os.environ.get(env_var)
        if branch_name:
            return branch_name
    return ''
def get_branch_name() -> str:
    """
    Get the current branch name, even in detached HEAD state.

    Returns:
        The branch name as a string.

    Raises:
        RuntimeError: If the branch name cannot be determined.
    """
    try:
        # Try to get the branch name using symbolic-ref
        branch_name = subprocess.check_output(
            ['git', 'symbolic-ref', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        # If symbolic-ref fails (e.g., detached HEAD), fall back to name-rev
        try:
            ref_name = subprocess.check_output(
                ['git', 'name-rev', '--name-only', 'HEAD'],
                stderr=subprocess.DEVNULL
            ).decode('utf-8').strip()
            if (ref_name.startswith('remotes/') or
                ref_name.startswith('refs/')):
                chunks = ref_name.split('/')
                branch_name = '/'.join(chunks[2:])
        except subprocess.CalledProcessError:
            raise RuntimeError('Error: failed to determine the branch name. Are you in a git repository?')

    if not branch_name:
        raise RuntimeError(f'Error: cannot analyze branch name out of {ref_name}!')
    return branch_name


def main(argv: Sequence[str] | None = None) -> int:
    """
    Main function for the branch_check script. Parses the command-line
    arguments, then checks the name of the branch against the allowed/denied
    patterns.  A branch name must match at least one of the allowed patterns
    and must not match any of the denied patterns.

    Args:
      argv: A sequence of command-line arguments. If None, sys.argv[1:] will be
      used.

    Returns:
      An integer representing the exit code. 0 indicates success, while non-zero
      values indicate errors.
    """
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog='branch_check', description='Check branch name against allow/deny patterns')

    parser.add_argument(
        '-a', '--allow',
        dest='allow',
        action='append',
        help='Regular expression that branch name should match, can be repeated.'
    )

    parser.add_argument(
        '-d', '--deny',
        dest='deny',
        action='append',
        help='Regular expression that branch name should not match, can be repeated.'
    )

    # Parse the command-line arguments and pick good defaults
    args = parser.parse_args(argv)
    allow_patterns = args.allow or DEFAULT_ALLOWED_PATTERNS
    deny_patterns = args.deny or DEFAULT_DENIED_PATTERNS

    # Detect the current branch name
    try:
        branch_name = get_forge_branch()
        if branch_name == '':
            branch_name = get_branch_name()
    except RuntimeError as e:
        print(e)
        return 1

    # Check if the branch name matches any of the allowed patterns
    if not any(re.match(pattern, branch_name) for pattern in allow_patterns):
        print(f'Branch name "{branch_name}" does not match any of the allowed patterns: {allow_patterns}')
        return 1
    # Check if the branch name matches any of the denied patterns
    if any(re.match(pattern, branch_name) for pattern in deny_patterns):
        print(f'Branch name "{branch_name}" matches a denied pattern: {deny_patterns}')
        return 1
    print(f'Branch name "{branch_name}" is valid.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
