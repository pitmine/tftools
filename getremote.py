#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Get remote name from terraform state file."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json
import os
import sys

TF_STATE = str('.terraform/terraform.tfstate')

# Python 2/3 compatibility
try:
    # noinspection PyCompatibility,PyUnresolvedReferences
    STRING = basestring             # pylint: disable=E0602
except NameError:
    STRING = str


def name(statefile=TF_STATE):
    """Extract Atlas remote name from Terraform remote state JSON file.

    :param statefile: Filename for Terraform state file
    :type statefile: str
    :returns: str Atlas remote in user-org/env format e.g. 'jane_doe/example'
    :returns: None if the state is local
    :raises: ValueError if the state file is missing or cannot be parsed
    """
    try:
        with open(statefile) as tf_state:
            state = json.loads(tf_state.read())
            remote = state.get('remote', None)
            if remote is None:
                return None
            remote_name = remote['config']['name']
            if remote_name.count('/') == 1 and isinstance(remote_name, STRING):
                return remote_name
            raise TypeError()

    except (TypeError, AttributeError, KeyError):
        # remote,config not dict; name not "a/b" string; config,name missing
        raise ValueError('Unknown structure in Terraform state')

    except ValueError:  # returned by json.loads on JSON syntax error
        raise ValueError('Unknown format in Terraform state')

    except IOError as err:
        if statefile == TF_STATE and os.path.isdir(os.path.dirname(TF_STATE)):
            # default name, directory exists, but not TF_STATE => not remote
            return None
        raise ValueError(err)


def main():
    """Print Atlas remote name.

    :returns: int Exit code (1 on format error/file not found, 2 if not remote)
    """
    try:
        remote_name = name()
        if remote_name is None:
            print('State is local', file=sys.stderr)
            return 2
        print(remote_name)
        return 0

    except ValueError as err:
        if str(err).endswith("'"):
            print(err, file=sys.stderr)
        else:
            print("{0}: '{1}'".format(err, TF_STATE), file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
