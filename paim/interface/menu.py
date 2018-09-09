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

"""Print the program menu and checks for a valid input."""

def print_menu():
    """Print the program menu and checks for a valid input.

    Returns:
        selection {integer} -- selected option
    """
    menu = {}
    menu['1'] = "Start simulator"
    menu['2'] = "Update variables and run simulation"
    menu['0'] = "Exit."

    selection = -1

    options = menu.keys()

    print("\n############### PAIM ###############")

    for entry in options:
        # print("{} - {}".format(entry, menu[entry]))
        print(f"{entry} - {menu[entry]}")

    while True:
        try:
            selection = int(input("\n-> Please Select: "))

            # Check for valid input
            if 0 <= selection < len(menu):
                break

        except ValueError:  # if selection is NaN
            pass

        print(f"Invalid option. It must be a number between 0 and {len(menu) - 1}")

    return selection
