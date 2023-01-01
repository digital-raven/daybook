=================
 daybook-convert
=================

-------------------------------
Convert a CSV to daybook format
-------------------------------

.. include:: _manual-section.rst


SYNOPSIS
========

**daybook** [global-opts] **convert** [options]

DESCRIPTION
===========
This command converts the headings in a CSV.

EXAMPLES
========
Let's say your bank exported an example CSV in the following format.

::

    Date, Amount, Description, Category
    10/01/2022,14.56,LOCAL GROCERY STORE,food

This aren't headings that are compatible with daybook. Let's set a rules file
to convert them. This file is in yaml format where the keys are the headings
expected by daybook, and the values are the corresponding headings in the
example non-compliant CSV. Case matters.

::

    ---
    date: Date
    dest: Description
    amount: Amount

The "Category" heading will be ignored because it isn't in the rules. To convert
this csv we would run ``daybook convert --csvs mycsv.csv --rules myrules.yaml``
and our output would be...

::

    date, dest, amount
    10/01/2022,LOCAL GROCERY STORE,14.56

The order will be the same as in the rules file. Use redirection to save this
output to a file.

OPTIONS
=======
These options must be specified after the subcommand.

**--csvs** *CSV* [*CSV*...]
        List of CSV files to convert.

**--rules** *rules-file*
        Rules file to use. See above for examples.

**-h**, **--help**
        Display a help message and exit.

SEE ALSO
========
daybook(1)
