# This file is part of HEROiC
# Copyright (C) 2018 Miguel Fernandes
#
# HEROiC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HEROiC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Helpers to format text."""

import math


def eng_string(x, sig_figs=3, si=True):
    """Returns the input value formatted in a simplified engineering
    format, i.e. using an exponent that is a multiple of 3.

    Copied from: link<https://stackoverflow.com/questions/17973278/python-decimal
                 -engineering-notation-for-mili-10e-3-and-micro-10e-6>

    Arguments:
        x {float|int} -- Value to format

    Keyword Arguments:
        sig_figs {int} -- number of significant digits (default: 3)
        si {bool} -- use SI suffix for exponent, e.g. k instead of e3,
                     n instead of e-9 etc. (default: True)

    Returns:
        str -- the formatted value
    """

    x = float(x)
    sign = ''
    if x < 0:
        x = -x
        sign = '-'
    if x == 0:
        exp = 0
        exp3 = 0
        x_3 = 0
    else:
        exp = int(math.floor(math.log10(x)))
        exp3 = exp - (exp % 3)
        x_3 = x / (10 ** exp3)
        x_3 = round(x_3, -int(math.floor(math.log10(x_3)) - (sig_figs-1)))
        if x_3 == int(x_3):  # prevent from displaying .0
            x_3 = int(x_3)

    if si and exp3 >= -24 and exp3 <= 24 and exp3 != 0:
        exp3_text = 'yzafpnum kMGTPEZY'[exp3 // 3 + 8]
    elif exp3 == 0:
        exp3_text = ''
    else:
        exp3_text = 'e%s' % exp3

    return ('%s%s%s') % (sign, x_3, exp3_text)
