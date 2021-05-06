#!/usr/bin/python3 -u
"""
Clones or updates local copies of all the specified organization's repos

Execute in a new directory, or one already containing one or more of the
organization's repos.
"""

import os
from pathlib import Path
import subprocess

# Github module https://github.com/jacquev6/PyGithub
from github import Github

# MantisBT scripts config
import config
from config import cfg

github_org = config.ORG_PLUGINS


def run_git(command, *args):
    cmd = ['git', command, *args]
    return subprocess.run(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          check=True)

def main():
    print("Retrieving all plugins from '{}' organization".format(github_org))

    print("Connecting to Github")
    gh = Github(cfg.github['token'])
    org = gh.get_organization(github_org)

    # Process all repos
    repos = org.get_repos()
    print("{0} plugin repositories found".format(repos.totalCount))
    count = 0
    errors = {}
    for repo in org.get_repos():
        if count > 5:
            break
        count += 1

        print("\nProcessing plugin '{}'".format(repo.name))

        # Local repo exists, change to default branch
        if Path(repo.name).is_dir():
            print("  Updating local repository")
            os.chdir(repo.name)

            print("    Checkout default branch '{}'"
                  .format(repo.default_branch))
            try:
                run_git('checkout', repo.default_branch)
            except subprocess.CalledProcessError as e:
                msg = e.stderr.strip().decode('UTF-8')
                continue

            print("    Pulling from remote")
            try:
                run_git('pull')
            except subprocess.CalledProcessError as e:
                msg = e.stderr.strip().decode('UTF-8')
                print(msg)
                errors[repo.name] = msg

        # Cloning repo if not found locally
        else:
            print("  Local repo not found, cloning...")
            run_git('clone', repo.clone_url)
            os.chdir(repo.name)

        os.chdir('..')

    print()
    if errors:
        print("Errors occured while processing the following plugins")
        for plugin, err in errors.items():
            print("- {0}\n{1}\n".format(plugin, err))

    print("{0} plugins processed".format(count))


if __name__ == "__main__":
    main()
