#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Get metadata from configuration drive.

Prints metadata values as 'key="value"' so that shell scripts can e.g.
`eval "$(config-meta-env.py)"` to get all metadata as (non-exported) variables.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json
import os
import subprocess
import sys
import tempfile

# '2013-10-17' is pinned config drive API revision, 'latest' might work as well
META_NAME = str(os.path.join('openstack', '2013-10-17', 'meta_data.json'))
CONFIG_DRIVE = '/dev/disk/by-label/config-2'


def metadata(meta_name=None):
    """Mount configuration drive and load JSON metadata.

    :param meta_name: Filename for metadata JSON file
    :type meta_name: str
    :returns: parsed JSON metadata from file
    :rtype: dict
    :raises ValueError: if config drive or metadata file are missing/corrupted
    """
    mountpoint = None
    mounted = False
    try:
        if meta_name is None:
            mountpoint = tempfile.mkdtemp(prefix=str('confdrv.'))
            subprocess.check_output(['mount', '-r', CONFIG_DRIVE, mountpoint],
                                    stderr=subprocess.STDOUT)
            mounted = True
            meta_name = os.path.join(mountpoint, META_NAME)

        with open(meta_name) as meta_data:
            meta = json.loads(meta_data.read())
            if isinstance(meta, dict):
                return meta
            raise TypeError()

    except (TypeError, KeyError):  # meta missing or not dict
        raise ValueError('Unknown structure in metadata file')

    except ValueError:  # returned by json.loads on JSON syntax error
        raise ValueError('Unknown format in metadata file')

    except IOError as err:
        raise ValueError(err)

    except subprocess.CalledProcessError as err:
        raise ValueError(err.output.rstrip())

    finally:
        try:
            if mountpoint is not None:
                if mounted:
                    subprocess.check_output(['umount', mountpoint])
                subprocess.check_output(['rmdir', mountpoint])
        except subprocess.CalledProcessError:
            pass


def main():
    """Print OpenStack metadata key=value pairs from configuration drive.

    :returns: int Exit code (1 on format error/file not found/access error)
    """
    filename = None
    key = 'meta'  # metadata key for user-provided metadata (tags) dict
    try:
        if len(sys.argv) > 3:
            raise ValueError('usage: ' + sys.argv[0] + ' [ [FILE] KEY ]')
        elif len(sys.argv) > 2:
            filename = sys.argv[1]
            key = sys.argv[2]
        elif len(sys.argv) > 1:
            key = sys.argv[1]
        meta_data = metadata(filename)
        if isinstance(meta_data[key], dict):
            for subkey in meta_data[key].keys():
                print('{0}={1}'.format(subkey, meta_data[key][subkey]))
        else:
            print('{0}={1}'.format(key, meta_data[key]))
        return 0

    except ValueError as err:
        print(err, file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
