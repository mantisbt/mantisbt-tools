#!/usr/bin/python -u
"""
Uses Github API to grant write access to all of mantisbt-plugins organization
to the teams specified in config file
"""

import sys

# PyGithub library https://github.com/PyGithub/PyGithub
from github import Github, GithubException

# Configuration variables
import config
from config import cfg


def retrieve_teams(org):
    """
    Returns a list of Team objects for the names defined in github_teams
    that have fewer repositories than the specified organization
    """
    teams = []
    for team in org.get_teams():
        if (
            team.name in cfg.github['teams'] and
            team.repos_count < org.public_repos
           ):
            teams.append(team)
    return teams


def main():
    print "Connecting to Github as '{0}'".format(cfg.github['user'])
    g = Github(cfg.github['user'], cfg.github['password'])

    # Organization
    org = g.get_organization(config.ORG_PLUGINS)
    print "Retrieving organization '{0}' ({1})".format(org.login, org.name)

    # Teams
    print "Retrieving teams"
    try:
        teams = retrieve_teams(org)
    except GithubException as err:
        if err.status == 401:
            print "This script requires authentication with a privileged " \
                "account to access and update the organization's team."
            print "Please update the configuration as appropriate"
        else:
            print "Unknown error", (err)
        sys.exit(1)
    if not teams:
        print "The teams", ', '.join(cfg.github['teams']),
        print "already have write access to all repositories"
        sys.exit()

    # Check that the team grants access to each of the org's repo
    # Add write access if not
    print "Processing {0} plugins for {1} teams".format(
        org.public_repos,
        len(teams)
        )
    count = 0
    for repo in org.get_repos():
        for team in teams:
            if not team.has_in_repos(repo):
                count += 1
                print "Grant team '{0}' write access to plugin '{1}'".format(
                    team.name,
                    repo.name
                    )
                team.set_repo_permission(repo, 'push')

    print "{0} plugins processed".format(count)
    print "Done"


if __name__ == "__main__":
    main()
