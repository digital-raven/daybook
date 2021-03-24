=================
 daybook-balance
=================

--------------------------
Check balances of accounts
--------------------------

.. include:: _manual-section.rst

SYNOPSIS
========

**daybook** [global-opts] **balance** [options]

DESCRIPTION
===========
This command prints balances of accounts based on the available transactions.
The transactions can be loaded either from daybookd or from local CSV files.

OPTIONS
=======
These options must be specified after the subcommand.

**-h**, **--help**
        Display a help message and exit.

.. include:: _daybook-csv-opts.rst
.. include:: _daybook-server-opts.rst
.. include:: _daybook-filter-opts.rst

EXAMPLES
========
To print balances based on transactions provided by a daybookd, simply run
``daybook balance``. The server settings in the default configuration file
will be used.

To use local CSV files, use the ``--csvs`` option like so...

::

    daybook balance --csvs ./ledger

SEE ALSO
========
daybook(1)
