# This file is part of PAIM
# Copyright (C) 2018 Miguel Fernandes
#
# PAIM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PAIM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""PAIM entry point."""

import argparse
import os.path
import sys

from paim import paim


class CustomFormatter(argparse.HelpFormatter):
    """Custom formatter for the "argparse" help.

    Arguments:
        argparse {module} -- argparse

    Returns:
        str -- text to print
    """

    def _format_action_invocation(self, action):
        """Format the 'argparse' help.

        Arguments:
            action {object} -- 'argparse' action

        Returns:
            str -- text to print
        """
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            # change to
            #    -s, --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    #parts.append('%s %s' % (option_string, args_string))
                    parts.append('%s' % option_string)
                parts[-1] += ' %s' % args_string
            return ', '.join(parts)


def main():
    """PAIM main function."""
    description = 'Python optimizer for circuit design and optimization using Cadence Virtuoso.'
    parser = argparse.ArgumentParser(description=description, formatter_class=CustomFormatter)

    parser.add_argument('project_file', metavar='CFG', help='file with the optimizer parameters')

    parser.add_argument(
        '-c',
        '--checkpoint',
        metavar='FILE',
        dest='checkpoint_file',
        default=None,
        help='continue the optimization from a checkpoint file')

    parser.add_argument(
        '-d',
        '--debug',
        dest='debug',
        default=False,
        action='store_true',
        help='run the program in debug mode')

    args = parser.parse_args()

    project_file = args.project_file
    checkpoint_file = args.checkpoint_file
    debug = args.debug

    # Check if project_file exists
    if not os.path.isfile(project_file):
        print("[ERROR] Invalid CONFIG file path. Exiting the program...")
        return
    # Check if checkpoint file exists
    if checkpoint_file and not os.path.isfile(checkpoint_file):
        print("[ERROR] Invalid CHECKPOINT file path. Exiting the program...")
        return

    # Run the optimizer
    sys.exit(paim.run_paim(project_file, checkpoint_file, debug))


if __name__ == "__main__":
    main()
