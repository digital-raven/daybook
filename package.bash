#!/usr/bin/env bash
################################################################################
# help create distribution for daybook.
################################################################################

version="$(grep Version DEBIAN/control | awk '{print $2}')"
pkgname="daybook_$version"

# Make man pages
cd docs/man
make
cd - > /dev/null

if [ "$1" == "python3" ]
then
    python3 setup.py bdist_wheel
elif [ "$1" == "gz" ]
then
    python3 setup.py bdist --format=gztar
elif [ "$1" == "clean" ]
then
    rm -rf .pybuild *.deb daybook_*/ dist/ *.egg-info build/ debian/ *.rpm
    cd docs/man
    make clean
    exit 0
else
    echo "Did nothing"
fi
