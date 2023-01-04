=========
 daybook
=========

Hello and welcome to daybook, a command line accounting program.

Documentation
=============
Read the man pages in ``./docs/man`` for usage and examples. These will
be installed to ``/usr/share/man`` if installing from deb or to
``~/.local/usr/share/man`` if using pip with the ``--user`` option. Update
your ``MANPATH`` accordingly.

Required packages for a developer
=================================
The machine used to develop this software was running Ubuntu 20.04. The
following packages are needed to build, develop, and package releases on
this operating system.

::

    python3-venv python3-pip dh-python docutils-common

Maintenance
===========
When releasing, update the version in DEBIAN/control and setup.py.

Building and installation
=========================
Use the ``package.bash`` script to create releases. It can release the software
as a python wheel, deb, rpm, or simply a gz archive with the respective
commands.

::

    ./package.bash python
    ./package.bash deb
    ./package.bash rpm
    ./package.bash gz

    # Clean the directory.
    ./package.bash clean

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
