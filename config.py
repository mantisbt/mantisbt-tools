#!/usr/bin/python3 -u
"""
Configuration for various MantisBT utility scripts
"""

import yaml
import collections


# Constants
ORG_MANTIS = 'mantisbt'
ORG_PLUGINS = 'mantisbt-plugins'


class Config(dict):
    """
    The Config class extends dict wrapper allowing its keys to be accessed as
    attributes for convenience.
    """
    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(name)


def __update(base, upd):
    """
    Recursively update 'base' dict with corresponding values in 'upd'
    """
    for key, value in upd.items():
        if isinstance(value, collections.Mapping):
            base[key] = __update(base.get(key, {}), value)
        else:
            base[key] = upd[key]
    return base


def __read_config():
    """
    Read YML config files and return the data
    """

    # Read default configuration values
    with open("config_defaults.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)

    # Read local settings
    with open("config.yml", 'r') as ymlfile:
        cfg = __update(cfg, yaml.load(ymlfile, Loader=yaml.BaseLoader))

    return Config(cfg)


cfg = __read_config()
