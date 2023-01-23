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

Maintenance
===========
Update the CHANGELOG when cutting a new release, then create and push a git tag
named after the new version. This project's packaging script and setup.py will
automatically determine the version based on git-describe.

Building and installation
=========================
Clone this repo, checkout a release tag, and run these commands.

::

    ./package.bash python3
    pip3 install --user .
    ./package.bash clean

Manpages will be installed to ``$HOME/.local/usr/share/man`` and the completion
script will be installed under ``$HOME/.local/etc/bash_completion.d``. Update your
``MANPATH`` and bashrc accordingly.

Testing and developer usage
===========================
Run these commands to install daybook to a virtual environment.

::

    python3 -m venv ./venv
    . ./venv/bin/activate
    python3 ./setup.py
    pip3 install -e .
    daybook

Use the following command to run unit tests.

::

    python3 -m unittest
