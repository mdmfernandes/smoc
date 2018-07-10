# -*- coding: utf-8 -*-

"""Handling of files"""

import yaml


def read_yaml(fname='../config/config.yaml'):
    """Read the given file using YAML.

    Arguments:
        fname {string} -- the file name.
    Returns:
        cfg {any} -- the object returned by YAML.
    """
    with open(fname, 'r') as f:
        cfg = yaml.load(f)

    return cfg
