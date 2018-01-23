#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Optimizer root module"""

from utils.file import read_yaml
from interface.client import Client

import sys


def main():
    """Optimizer main function"""

    server = read_yaml()['server']
    host = server['host']
    port = server['port']

    try:
        client = Client(host, port)

        client.run()

    except (OSError, KeyboardInterrupt) as err:
        print("ClientError: {0}".format(err))
    


if __name__ == "__main__":
    main()
