==============
 daybook-dump
==============

----------------------------
Print transactions to stdout
----------------------------

.. include:: _manual-section.rst

SYNOPSIS
========

**daybook** [global-opts] **dump** [options]

DESCRIPTION
===========
This command prints transactions to stdout. The dump is a valid Daybook CSV
and can therefore be re-imported later.

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
``daybook dump``. The server settings in the default configuration file
will be used.

To use local CSV files, use the ``--csvs`` option like so...

::

    daybook dump --csvs ./ledger

The dump command can be used to consolidate records into single files, since
duplicate transactions will automatically be omitted from the dump. If a user
wanted to create a special CSV for all food transactions, they could do it
by following the example below.

::

    daybook dump --csvs ./ledger --accounts expense.food > expense.food.csv

SEE ALSO
========
daybook(1)
