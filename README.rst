=========
 daybook
=========

Hello and welcome to daybook, a command line accounting program.

Documentation
=============
Read the man pages in ``./docs/man`` for usage and examples.

Required packages for a developer
=================================
The machine used to develop this software was running Ubuntu 20.04. The
following packages are needed to build, develop, and package releases on
this operating system.

::

    python3-venv python3-pip docutils-common

Docker may also be required depending on your environment. Read below.

Maintenance
===========
Update the CHANGELOG and version in setup.py when cutting a new release.
Build it with ``make`` and push to PyPi with ``make release``

Building and installation
=========================
Clone this repo, checkout a release tag, and run these commands.

::

    make
    pip3 install --user .

Manpages will be installed to ``$HOME/.local/usr/share/man`` and the completion
script will be installed under ``$HOME/.local/etc/bash_completion.d``. Update your
``MANPATH`` and bashrc accordingly.

If you are not capable of installing daybook in this way, then there is a
Dockerfile and script which will produce a compatible environment.

::

    cd docker
    make
    ./daybook.bash

Testing and developer usage
===========================
Run these commands to install daybook to a virtual environment. You will only
be able to use daybook in the venv if it's been previously installed using
``pip3 install --user .`` . This is because the datafiles in setup.py will not
install in the venv, but are required to run daybook.

::

    python3 -m venv ./venv
    . ./venv/bin/activate
    pip3 install -e .
    daybook

Use the following command to run unit tests.

::

    python3 -m unittest
