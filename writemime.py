#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate MIME multi-part user-data file.

Adapted from bin/write-mime-multipart
http://bazaar.launchpad.net/~cloud-utils-dev/cloud-utils/trunk/revision/266.

Largely taken from python examples at
http://docs.python.org/library/email-examples.html
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import gzip
import os
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MAPPINGS = {
    '#include': 'text/x-include-url',
    '#include-once': 'text/x-include-once-url',
    '#!': 'text/x-shellscript',
    '#cloud-config': 'text/cloud-config',
    '#cloud-config-archive': 'text/cloud-config-archive',
    '#upstart-job': 'text/upstart-job',
    '#part-handler': 'text/part-handler',
    '#cloud-boothook': 'text/cloud-boothook'
}


# noinspection PyRedundantParentheses
def try_decode(data):
    """Convert file (first line) data to Unicode if possible.

    :param data: (first line) contents of part file
    :type data: bytes
    :return: tuple with Unicode text indication and (decoded or binary) data
    :rtype: tuple(bool, str)
    """
    try:
        return (True, data.decode())
    except UnicodeDecodeError:
        return (False, data)


def get_type(fname, deftype):
    """Determine MIME type of file based on first line contents.

    :param fname: filename to examine for MIME type
    :type fname: str
    :param deftype: default type for text (decodable Unicode) contents
    :type deftype: str
    :return: MIME type for file
    :rtype: str
    """
    rtype = deftype

    with open(fname, 'rb') as partfile:
        (can_be_decoded, line) = try_decode(partfile.readline())

    if can_be_decoded:
        # slist is sorted longest first
        slist = sorted(list(MAPPINGS.keys()),
                       key=lambda e: 0 - len(e))
        for sstr in slist:
            if line.startswith(sstr):
                rtype = MAPPINGS[sstr]
                break
    else:
        rtype = 'application/octet-stream'

    return rtype


def main():
    """Generate MIME multi-part user-data file from specified parts.

    :raises IOError: (FileNotFoundError) when specified part file not found
    :raises IOError: (PermissionError) when specified part file cannot be read
    """
    outer = MIMEMultipart()

    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '--output', dest='output', default='-',
                        help='write output to FILE [default standard output]',
                        metavar='FILE')
    parser.add_argument('-z', '--gzip', dest='compress', default=False,
                        help='compress output', action='store_true')
    parser.add_argument('-d', '--default', dest='deftype', default='text/plain',
                        help="default text MIME type [default '%(default)s']")
    parser.add_argument('--delim', dest='delim', default=':',
                        help="MIME suffix delimiter [default '%(default)s']")

    parser.add_argument('parts', nargs='+',
                        help='part filename and optional MIME type',
                        metavar='PARTFILE[:MIME/TYPE]')

    args = parser.parse_args()

    for arg in args.parts:
        argtype = arg.split(args.delim, 1)
        path = argtype[0]
        if len(argtype) > 1:
            mtype = argtype[1]
        else:
            mtype = get_type(path, args.deftype)

        maintype, subtype = mtype.split('/', 1)
        if maintype == 'text':
            partfile = open(path)
            # Note: we should handle calculating the charset
            msg = MIMEText(partfile.read(), _subtype=subtype)
            partfile.close()
        else:
            partfile = open(path, 'rb')
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(partfile.read())
            partfile.close()
            # Encode the payload using Base64
            encoders.encode_base64(msg)

        # Set the filename parameter
        # noinspection PyUnresolvedReferences
        msg.add_header('Content-Disposition', 'attachment',
                       filename=os.path.basename(path))

        outer.attach(msg)

    if args.output is '-':
        if hasattr(sys.stdout, 'buffer'):
            # We want to write bytes not strings
            ofile = sys.stdout.buffer  # pylint: disable=E1101
        else:
            ofile = sys.stdout
    else:
        ofile = open(args.output, 'wb')

    if args.compress:
        gfile = gzip.GzipFile(fileobj=ofile, filename=args.output)
        gfile.write(outer.as_string().encode())
        gfile.close()
    else:
        ofile.write(outer.as_string().encode())

    ofile.close()

if __name__ == '__main__':
    main()

# vi: ts=4 expandtab
