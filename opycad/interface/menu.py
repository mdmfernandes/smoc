# -*- coding: utf-8 -*-
"""Print the program menu and checks for a valid input"""

def print_menu():
    """Print the program menu and checks for a valid input

    Returns:
        selection {integer} -- selected option
    """
    menu = {}
    menu['1'] = "Start simulator"
    menu['2'] = "Update variables and run simulation"
    menu['0'] = "Exit."

    selection = -1

    options = menu.keys()

    print("\n############### OPYCAD ###############")

    for entry in options:
        # print("{} - {}".format(entry, menu[entry]))
        print(f"{entry} - {menu[entry]}")

    while True:
        try:
            selection = int(input("\n-> Please Select: "))

            # Check for valid input
            if selection >= 0 and selection < len(menu):
                break

        except ValueError:  # if selection is NaN
            pass

        print(f"Invalid option. It must be a number between 0 and {len(menu) - 1}")

    return selection
