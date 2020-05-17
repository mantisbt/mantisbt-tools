#!/usr/bin/python -u
"""
Clones or updates local copies of all the specified organization's repos

Execute in a new directory, or one already containing one or more of the
organization's repos.
"""

import os
from os import path
import subprocess

# Github module https://github.com/jacquev6/PyGithub
from github import Github

# MantisBT scripts config
import config
from config import cfg

github_org = config.ORG_PLUGINS


def main():
    print "Retrieving all plugins from '%s' organization" % github_org

    print "Connecting to Github"
    gh = Github(cfg.github['token'])
    org = gh.get_organization(github_org)

    # Process all repos
    for repo in org.get_repos():
        print "\nProcessing plugin '%s'" % repo.name

        # Local repo exists, change to default branch
        if path.isdir(repo.name):
            print "  Updating local repository"
            os.chdir(repo.name)
            print "    Checkout default branch '%s'" % repo.default_branch
            subprocess.check_call('git checkout %s' % repo.default_branch,
                                  shell=True)
            print "    Pulling from remote"
            subprocess.check_call('git pull', shell=True)

        # Cloning repo if not found locally
        else:
            print "  Local repo not found, cloning..."
            subprocess.check_call('git clone %s' % repo.clone_url, shell=True)
            os.chdir(repo.name)

        os.chdir('..')

    print "\nDone"


if __name__ == "__main__":
    main()
