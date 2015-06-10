#!/bin/sh

bumpversion --verbose --commit --tag release_type
python setup.py sdist bdist_wheel
bumpversion --verbose --commit --no-tag patch
