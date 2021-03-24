=================
 daybook-expense
=================

--------------------------
Generate an expense report
--------------------------

.. include:: _manual-section.rst

SYNOPSIS
========

**daybook** [global-opts] **expense** [options]

DESCRIPTION
===========
This command prints a basic expense report to stdout. The default date range
of the transactions used to create this report is the current month. This
behavior may be overridden using command line options.

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
To print the report based on transactions provided by a daybookd, simply run
``daybook expense``. The server settings in the default configuration file
will be used.

To use local CSV files, use the ``--csvs`` option like so...

::

    daybook expense --csvs ./ledger

SEE ALSO
========
daybook(1)
