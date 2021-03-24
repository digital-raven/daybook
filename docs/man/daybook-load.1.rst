==============
 daybook-load
==============

---------------------------------
Load transactions into a daybookd
---------------------------------

.. include:: _manual-section.rst

SYNOPSIS
========

**daybook** [global-opts] **load** [options]

DESCRIPTION
===========
The "load" subcommand loads transactions from local CSVs and into a listening
daybookd. These transactions can then be read out using commands like
``daybook dump`` or ``daybook balance``.

OPTIONS
=======
These options must be specified after the subcommand.

**-h**, **--help**
        Display a help message and exit.

.. include:: _daybook-csv-opts.rst
.. include:: _daybook-server-opts.rst
.. include:: _daybook-filter-opts.rst

SEE ALSO
========
daybook(1)
