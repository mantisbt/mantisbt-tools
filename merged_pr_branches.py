#!/usr/bin/python3 -u
"""
Retrieve a list of branches that can safely be deleted.

Once a PR has been merged, its reference branch is in most cases no longer
needed. GitHub offers a button to delete it, but this is a manual task and if
not done right away developers forget to do it and these branches tends to
pile up.

This script checks all branches in the specified developer's repository against
successfully merged PRs that were submitted by that developer in the reference
repository. If one or more matching references are found, it prints a command
that can be used to delete the no-longer needed branches.
"""

import getopt
from os import path
import sys

# Github module https://github.com/jacquev6/PyGithub
from github import Github, GithubException, BadCredentialsException

# MantisBT scripts config
from config import cfg

# Default values for command-line options - Edit as appropriate
# GitHub ID of the target org
target_org = 'mantisbt'
# Repository name
repo_name = 'mantisbt'
# GitHub ID of the PR's author
author = None

# Command-line options
short_options = "hr:t:"
long_options = ["help", "author=", "repository=", "target="]

# GitHub API object
gh: Github


def get_options():
    """
    Process command-line options.
    Option values are stored in global variables below.
    """
    global repo_name, target_org, author

    def usage():
        print("""
Identifies branches merged via pull request still present in a repository

Usage: {0} [options] <author>

Options:
    -h | --help               Show this usage message

    -r | --repository <repo>  Repository name (default: {1})
    -t | --target <name>      GitHub ID of the target org/user (default: {2})
"""
              .format(path.basename(__file__), repo_name, target_org))
    # end usage()

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:],
                                       short_options,
                                       long_options)
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    # Author is mandatory
    if len(args) < 1:
        usage()
        sys.exit(1)
    author = args[0]

    # Process options
    for opt, val in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ("-r", "--repository"):
            repo_name = val
        elif opt in ("-t", "--target"):
            target_org = val


def get_repo(user, repo):
    """
    Return a GitHub repository object
    """
    fullname = '{0}/{1}'.format(user, repo)

    try:
        repo = gh.get_repo(fullname)
    except BadCredentialsException:
        print("ERROR: invalid credentials - check token in config.yml")
        sys.exit(1)
    except GithubException:
        print("ERROR: repository '{}' not found".format(fullname))
        sys.exit(1)

    return repo


def main():
    get_options()

    print('Connecting to GitHub')
    global gh
    gh = Github(cfg.github['token'])

    # Retrieve the list of branches in the author's repository
    author_repo = get_repo(author, repo_name)
    refs = author_repo.get_git_refs()
    branches = list(ref.ref.replace('refs/heads/', '')
                    for ref in refs if ref.ref.startswith('refs/heads/'))
    print('{} branches found in {}'.format(len(branches),
                                           author_repo.full_name))

    # Retrieve the list of all merged PRs submitted by given author in the
    # target organization's repository with a matching target branch
    target_repo = get_repo(target_org, repo_name)
    query = ' '.join('head:' + b for b in branches)
    qualifiers = {
        'repo': target_repo.full_name,
        'author': author,
        'type': 'pr',
        'is': 'merged'
        }
    merged_pr = gh.search_issues(query=query, **qualifiers)
    if merged_pr.totalCount == 0:
        print("No matching merged PR by {1} found in {0}"
              .format(target_repo.full_name, author))
        return
    else:
        print('{} matching merged pull requests found in {}'
              .format(merged_pr.totalCount, target_repo.full_name))

    print('Retrieving corresponding head branches (this may take a while)...')
    merged_branches = {}
    for pr in merged_pr:
        pr = pr.as_pull_request()
        merged_branches[pr.head.ref] = pr.number

    print('Identifying merged branches that could be deleted')
    branches_to_delete = []
    for branch in branches:
        if branch in merged_branches:
            branches_to_delete.append(branch)
    if len(branches_to_delete) > 0:
        print('{0} branches successfully merged in {2} still present in {1}'
              .format(len(branches_to_delete),
                      author_repo.full_name,
                      target_repo.full_name))
        print()
        print("Execute the following commands to delete them")
        print("REMOTE=###")
        print("git push $REMOTE --delete " + ' '.join(branches_to_delete))
        print("git fetch $REMOTE --prune")
    else:
        print('No merged branches were found in {0}'
              .format(author_repo.full_name))


if __name__ == "__main__":
    main()
