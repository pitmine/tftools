#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Install and activate pre-commit and its hooks into virtual environment."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys

# if sys.version_info[0] > 2 or sys.version_info[1] < 7:
#     print("Python 2.7 required")
#     sys.exit(1)

VENV_NAME = 'VIRTUAL_ENV'
VENV = ''
try:
    VENV = os.environ[VENV_NAME]
    if VENV == '':
        print("Environment variable '%s' is empty" % VENV_NAME)
        print('Please activate your virtualenv first')
        sys.exit(3)
    if not os.path.isdir(VENV):
        print("Virtual environment '%s' does not exist" % VENV)
        print('Please activate a valid virtualenv first')
        sys.exit(2)

except KeyError:
    print('No virtualenv defined')
    print('Please activate a virtualenv (with mkvirtualenv, workon, or pyenv)')
    sys.exit(1)

if os.system('git config diff.userdata.textconv $PWD/userdata_decode.py'):
    print('Problem configuring Git diff filter for userdata')

if os.system('pre-commit --version'):
    os.system('pip install pre-commit')

if os.system('pre-commit install'):
    print('Error setting up pre-commit hooks, try updating with '
          'pip install -U pre-commit')
    sys.exit(4)

if os.system('pre-commit run --all-files'):
    print('Problem running pre-commit hooks, check .pre-commit-config.yaml')
    sys.exit(5)

sys.exit(0)
