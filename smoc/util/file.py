# This file is part of SMOC
# Copyright (C) 2018  Miguel Fernandes
#
# SMOC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SMOC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""Handling of files."""

import pickle
import yaml


def read_yaml(fname):
    """Read the given file using YAML.

    Arguments:
        fname (str): file path.
    Returns:
        any: object returned by YAML.
    """
    if not fname:
        return False

    with open(fname, 'r') as f:
        cfg = yaml.load(f)

    return cfg


def read_pickle(fname):
    """Read a pickle file and load the content to a variable.

    Arguments:
        fname (str): name of the file to read from.

    Returns:
        obj: file content.
    """
    with open(fname, 'rb') as f:
        obj = pickle.load(f)
    return obj


def write_pickle(fname, obj):
    """Write a pickled representation of an object to a file.

    Arguments:
        fname (str): name of the file to write to.
        obj (obj): object to write.
    """
    with open(fname, 'wb') as f:
        pickle.dump(obj, f)
