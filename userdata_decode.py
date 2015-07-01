#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Expand Base64-encoded data in MIME multipart userdata files for Git diff.

Only parts with MIME type 'text' are expanded; furthermore, boundary strings
are normalized to '--==cloud-multi===='.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import base64
import re
import sys

BOUNDARY = '--==cloud-multi===='


def main():
    """Print MIME multipart userdata files with Base64 expansion."""
    try:
        if len(sys.argv) != 2:
            raise ValueError('usage: ' + sys.argv[0] + ' USERDATA_FILE')

        boundary = re.compile(r'^--==')
        content_type = re.compile(r'^Content-Type: *([^/]+)/', re.IGNORECASE)
        content_base64 = re.compile(r'^Content-Transfer-Encoding: base64$',
                                    re.IGNORECASE)
        coded = re.compile(r'^[A-Za-z0-9+/=]+$')
        is_text = False
        is_b64 = False
        with open(sys.argv[1]) as input_file:
            for line in input_file:
                line_len = len(line)
                if boundary.match(line):
                    print(BOUNDARY)
                elif is_text and is_b64 and (line_len <= 77 and
                                             0 == (line_len - 1) % 4 and
                                             coded.match(line) is not None):
                    print(base64.b64decode(line).decode('utf-8'), end='')
                else:
                    type_match = content_type.match(line)
                    if type_match is not None:
                        main_type = type_match.group(1)
                        is_b64 = False
                        if main_type.lower() == 'text':
                            is_text = True
                        else:
                            is_text = False
                    elif content_base64.match(line):
                        is_b64 = True

                    print(line, end='')

    except IOError as err:
        print(err, file=sys.stderr)
        return 1

    except ValueError as err:
        print(err, file=sys.stderr)
        return 2

    except TypeError as err:
        print(err, file=sys.stderr)
        return 3

    return 0


if __name__ == '__main__':
    sys.exit(main())
