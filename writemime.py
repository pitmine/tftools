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
import mimetypes
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

MIME_DEFTYPE = 'application/octet-stream'

# Preload some common script extensions into MIME types lookup
for ext in ('sh', 'py', 'rb'):
    mimetypes.add_type('text/x-shellscript', '.' + ext, strict=False)


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


def get_mimetype(filename, default_mime_type):
    """Determine MIME type of file based on first line contents or extension.

    If no specific MIME type can be guessed, and the file is decodable UTF-8
    (or ASCII) text, the provided default mime type is used; for non-text files,
    application/octet-stream is returned.

    :param filename: filename to examine for MIME type
    :type filename: str
    :param default_mime_type: default type for text (decodable UTF-8) file
    :type default_mime_type: str
    :return: MIME type for file
    :rtype: str
    """
    (mime_type, encoding) = mimetypes.guess_type(filename, strict=False)
    line = ''
    if mime_type is None:
        mime_type = default_mime_type
    if encoding is not None:
        can_be_decoded = False
    else:
        with open(filename, 'rb') as part_file:
            (can_be_decoded, line) = try_decode(part_file.readline())

    if can_be_decoded:
        # sorted_list is sorted longest first
        sorted_list = sorted(list(MAPPINGS.keys()), key=lambda e: 0 - len(e))
        for start_str in sorted_list:
            if line.startswith(start_str):
                mime_type = MAPPINGS[start_str]
                break
    elif mime_type is None or mime_type.startswith('text/'):
        mime_type = MIME_DEFTYPE

    return mime_type


def main():
    """Generate MIME multi-part user-data file from specified parts.

    :raises IOError: (FileNotFoundError) when specified part file not found
    :raises IOError: (PermissionError) when specified part file cannot be read
    """
    outer = MIMEMultipart(boundary='==cloud-multi' + ('==' * len(sys.argv)))

    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '--output', dest='output', default='-',
                        help='write output to FILE [default standard output]',
                        metavar='FILE')
    parser.add_argument('-z', '--gzip', dest='compress', default=False,
                        help='compress output', action='store_true')
    parser.add_argument('-d', '--default', dest='deftype', default='text/plain',
                        help="default text MIME type [default '%(default)s']")
    parser.add_argument('--delim', dest='delimiter', default=':',
                        help="MIME suffix delimiter [default '%(default)s']")

    parser.add_argument('parts', nargs='+',
                        help='part filename and optional MIME type',
                        metavar='PART_FILE[:MIME/TYPE]')

    args = parser.parse_args()

    for arg in args.parts:
        argtype = arg.split(args.delimiter, 1)
        path = argtype[0]
        if len(argtype) > 1:
            mtype = argtype[1]
        else:
            mtype = get_mimetype(path, args.deftype)

        maintype, subtype = mtype.split('/', 1)
        if maintype == 'text':
            with open(path) as partfile:
                # Note: we should handle calculating the charset
                msg = MIMEText(partfile.read(), _subtype=subtype)
        else:
            with open(path, 'rb') as partfile:
                msg = MIMEBase(maintype, subtype)
                msg.set_payload(partfile.read())
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
            output_file = sys.stdout.buffer  # pylint: disable=E1101
        else:
            output_file = sys.stdout
    else:
        output_file = open(args.output, 'wb')

    if args.compress:
        gzip_file = gzip.GzipFile(fileobj=output_file, filename=args.output)
        gzip_file.write(outer.as_string().encode())
        gzip_file.close()
    else:
        output_file.write(outer.as_string().encode())

    output_file.close()

if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except IOError as err:
        print('{0}: {1}'.format(os.path.basename(sys.argv[0]), err),
              file=sys.stderr)
        sys.exit(1)

# vi: ts=4 expandtab
