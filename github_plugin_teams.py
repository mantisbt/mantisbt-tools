#!/usr/bin/python3 -u
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


def retrieve_org_repos(org):
    """
    Returns a list of all of the org's repositories
    """
    repos = []
    for repo in org.get_repos():
        repos.append(repo)
    return repos


def retrieve_teams(org):
    """
    Returns a list of all Teams in the specified organization
    """
    teams = {}
    for team in org.get_teams():
        teams[team.name] = team
    return teams


def retrieve_config_teams(org_teams):
    """
    Returns a list of Team objects for the ones defined in github.teams config
    """
    config_teams = {}
    invalid = []
    for team in cfg.github['teams']:
        try:
            config_teams[team] = org_teams[team]
        except KeyError as err:
            invalid.append(team)
    if invalid:
        print("Unknown teams specified in configuration:", ', '.join(invalid))
        sys.exit(1)
    return config_teams


def retrieve_team_repos(team):
    """
    Returns a dictionary of repositories the team has access to, with the
    repository id as key
    """
    repos = {}
    for repo in team.get_repos():
        repos[repo.id] = repo
    return repos


def main():
    print("Connecting to Github as '{0}'".format(cfg.github['user']))
    g = Github(cfg.github['user'], cfg.github['password'])

    # Organization
    print("Retrieving organization '{0}'".format(config.ORG_PLUGINS))
    org = g.get_organization(config.ORG_PLUGINS)

    # Organization Teams
    print("Retrieving teams...",)
    try:
        teams = retrieve_teams(org)
    except GithubException as err:
        print
        if err.status == 401:
            print("This script requires authentication with a privileged "
                  "account to access and update the organization's team.")
            print("Please update the configuration as appropriate")
        else:
            print("Unknown error", (err))
        sys.exit(1)
    print("  {0} teams found in the organization".format(len(teams)))

    # Special teams with access to all repos
    config_teams = retrieve_config_teams(teams)
    print("  {0} global teams configured".format(len(config_teams)))

    # Remove special teams from global teams list
    for team in config_teams.keys():
        teams.pop(team)

    # Repositories
    print("Retrieving the organization's repositories...",)
    org_repos = retrieve_org_repos(org)
    print("  {0} found".format(len(org_repos)))

    # Process Special teams and check that they grant access
    # to each of the org's repo; add appropriate access if not
    for team in config_teams.values():
        print("Processing team '{0}'".format(team.name))
        count = 0
        access = cfg.github['teams'][team.name]

        print("  Retrieving repositories...",)
        team_repos = retrieve_team_repos(team)
        print(len(team_repos), "found")

        print("  Checking for missing access")
        for repo in org_repos:
            if repo.id not in team_repos:
                count += 1
                print("  Grant {0} access to plugin '{1}'".format(
                    access,
                    repo.name
                    ))
                team.set_repo_permission(repo, access)
        print("  {0} plugins processed".format(count))


if __name__ == "__main__":
    main()
