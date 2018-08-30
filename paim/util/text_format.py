# -*- coding: utf-8 -*-

"""Format text"""

import math


def eng_string(x, sig_figs=3, si=True):
    """Returns the input value formatted in a simplified engineering
    format, i.e. using an exponent that is a multiple of 3.

    Copied from: link<https://stackoverflow.com/questions/17973278/python-decimal
                 -engineering-notation-for-mili-10e-3-and-micro-10e-6>

    Arguments:
        x {float/int} -- Value to format

    Keyword Arguments:
        sig_figs {int} -- Number of significant digits (default: 3)
        si {bool} -- Use SI suffix for exponent, e.g. k instead of e3,
                     n instead of e-9 etc. (default: True)

    Returns:
        {string} -- The formatted value
    """

    x = float(x)
    sign = ''
    if x < 0:
        x = -x
        sign = '-'
    if x == 0:
        exp = 0
        exp3 = 0
        x3 = 0
    else:
        exp = int(math.floor(math.log10(x)))
        exp3 = exp - (exp % 3)
        x3 = x / (10 ** exp3)
        x3 = round(x3, -int(math.floor(math.log10(x3)) - (sig_figs-1)))
        if x3 == int(x3):  # prevent from displaying .0
            x3 = int(x3)

    if si and exp3 >= -24 and exp3 <= 24 and exp3 != 0:
        exp3_text = 'yzafpnum kMGTPEZY'[exp3 // 3 + 8]
    elif exp3 == 0:
        exp3_text = ''
    else:
        exp3_text = 'e%s' % exp3

    return ('%s%s%s') % (sign, x3, exp3_text)
