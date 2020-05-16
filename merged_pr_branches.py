#!/usr/bin/python -u
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

import os
from os import path
import subprocess
import sys

# Github module https://github.com/jacquev6/PyGithub
from github import Github, GithubException

# Edit the variables below as appropriate
github_token = None
target_org = 'mantisbt' # GitHub ID of the target org
author = ''             # GitHub ID of the PR's author
repo_name = 'mantisbt'  # Repository name


def get_repo(user, repo):
    '''
    Return a GitHub repository object
    '''
    fullname = '{0}/{1}'.format(user, repo)

    try:
        repo = gh.get_repo(fullname)
    except GithubException as e:
        print("ERROR: repository '{}' not found".format(fullname))
        sys.exit(1)

    return repo


def main():
    print('Connecting to GitHub')
    global gh
    gh = Github(github_token)

    # Retrieve the list of branches in the author's repository
    author_repo = get_repo(author, repo_name)
    refs = author_repo.get_git_refs()
    branches = list(ref.ref.replace('refs/heads/', '') for ref in refs if ref.ref.startswith('refs/heads/'))
    print('{} branches found in {}'.format(len(branches),
                                           author_repo.full_name))

    # Retrieve the list of all merged PRs submitted by given author in the
    # target organization's repository
    target_repo = get_repo(target_org, repo_name)
    merged_pr = gh.search_issues(query='', **{
        'repo':target_repo.full_name,
        'author':author,
        'type':'pr',
        'is':'merged'
        })
    print('{} merged pull requests found in {}'
          .format(merged_pr.totalCount, target_repo.full_name))

    print 'Retrieving corresponding head branches (this may take a while)...'
    merged_branches = {}
    for pr in merged_pr:
        pr = pr.as_pull_request()
        merged_branches[pr.head.ref] = pr.number

    print 'Identifying merged branches that could be deleted'
    print
    print 'Branch,Merged in PR'
    count = 0
    for branch in branches:
        if branch in merged_branches:
            count += 1
            print '{},{}'.format(branch, merged_branches[branch])
    print
    print('{} branches in {} have been merged in {}'
          .format(count, author_repo.full_name, target_repo.full_name))

if __name__ == "__main__":
    main()
