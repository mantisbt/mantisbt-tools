#!/usr/bin/python3 -u
"""
Helper script for mantisbt-plugins organization maintenance

Uses Github API to
- Create a team for each plugin, granting push access to it
- grant the "Special" teams specified in config file access to all plugins
  in the organization
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
    repos = {}
    for repo in org.get_repos():
        repos[repo.name] = repo
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
    print("Retrieving teams...", end=' ')
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
    print(len(teams), "found", end=', ')

    # Special teams with access to all repos
    config_teams = retrieve_config_teams(teams)
    print(len(config_teams), "global teams configured")

    # Remove special teams from global teams list
    for team in config_teams.keys():
        teams.pop(team)

    # Repositories
    print("Retrieving the organization's repositories...", end=' ')
    org_repos = retrieve_org_repos(org)
    print("{0} found".format(len(org_repos)))

    # Each repo should have a corresponding team granting push access to it.
    # Create it if it does not exist
    print("Checking for missing plugin teams...")
    count = 0
    for repo in org_repos.values():
        team_name = 'Plugin ' + repo.name
        if not team_name.lower() in map(str.lower, teams):
            print("  Creating team for '{0}'".format(repo.name))
            new_team = org.create_team(team_name, [repo], 'push', 'closed')
            count += 1
    print("  {0} plugin teams created".format(count))

    # Checking for "orphan" teams
    print("Checking for other, possibly orphan teams...")
    count = 0
    for team in teams:
        search = team.replace('Plugin ', '').lower()
        if not search in map(str.lower, org_repos):
            print(' ', team)
            count += 1
    print("  {0} Teams to check".format(count))

    # Process Special teams and check that they grant access
    # to each of the org's repo; add appropriate access if not
    for team in config_teams.values():
        print("Processing team '{0}'".format(team.name))
        count = 0
        access = cfg.github['teams'][team.name]

        print("  Retrieving repositories...", end=' ')
        team_repos = retrieve_team_repos(team)
        print("{0} found".format(len(team_repos)))

        print("  Checking for missing access")
        for repo in org_repos.values():
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
