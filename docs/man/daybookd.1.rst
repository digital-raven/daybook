==========
 daybookd
==========

-----------------------------
Host transactions on a server
-----------------------------

.. include:: _manual-section.rst

SYNOPSIS
========

**daybookd** [options]

DESCRIPTION
===========
daybookd is the server component of Daybook. It is a basic server that allows
hosting transactions in memory for potentially faster report generation than
repeated reads from CSVs in the file system.

When a daybook client calls "load", it will send transactions to a listening
daybookd. A ledger is created for the username specified by that client and
daybookd will save the password in memory. When a client wants to read
transactions back out, it must provide the same username and password
combination.

OPTIONS
=======
These options must be specified after the subcommand.

**--config** *CONFIG*
        Select custom configuration file. ~/.config/daybook/daybook.ini is
        used by default.

**--port** *PORT*
        Listen on a custom port instead of the port in the config file.

**-h**, **--help**
        Display a help message and exit.

EXAMPLES
========
To launch daybookd locally, simply run ``daybookd``. All relevent settings
will be read from the configuration file.

To load transactions to the server, use the load command from the client.

::

    daybook load --csvs ./ledger/asset.checking.csv

The transactions in the server can be read back out from Daybook's various
commands.

::

    daybook balance

SEE ALSO
========
daybook(1)
