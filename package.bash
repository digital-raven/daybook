#!/usr/bin/env bash
################################################################################
# help create distribution for daybook.
################################################################################

version="$(grep Version DEBIAN/control | awk '{print $2}')"
pkgname="daybook_$version"

if [ "$1" == "python3" ]
then
    python3 setup.py bdist_wheel
elif [ "$1" == "deb" ]
then
    pybuild --build
    pybuild --install
    mkdir $pkgname
    cp -r debian/tmp/* $pkgname
    cp -r DEBIAN $pkgname
    dpkg-deb --build ./$pkgname
elif [ "$1" == "rpm" ]
then
    python3 setup.py bdist_rpm \
        --release 1 \
        --group Applications/Productivity \
        --requires "python3 python3-argcomplete python3-PrettyTable>=0.7.2 python3-PrettyTable<1.0 python3-dateparser" \

#        --build-requires "python3-devel python3-argcomplete python3-docutils"

elif [ "$1" == "gz" ]
then
    python3 setup.py bdist --format=gztar
elif [ "$1" == "clean" ]
then
    rm -rf .pybuild *.deb daybook_*/ dist/ *.egg-info build/ debian/ *.rpm
else
    echo "Did nothing"
fi
