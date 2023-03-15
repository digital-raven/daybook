=================
 daybook-convert
=================

-------------------------------
Convert a CSV to daybook format
-------------------------------

.. include:: _manual-section.rst


SYNOPSIS
========

**daybook** [global-opts] **convert** *converter* [options]

DESCRIPTION
===========
This command converts a CSV to daybook format.

Daybook provides a framework for writing ones own converter function to
ease manual importing of CSVs from an institution. Users may write their
own converter modules by following the guidelines in this manpage, or
they may select one of the presets provided by daybook. Daybook searches
the locations specified in the ``DAYBOOK_CONVERTERS`` environment variable.

OPTIONS
=======
These options must be specified after the subcommand.

**--csvs** *CSV* [*CSV*...]
        List of CSV files to convert.

**-h**, **--help**
        Display a help message and exit.

EXAMPLES
========
Different financial institutions export their CSVs in different formats.
Daybook's convert function helps you maintain scripts for each one so
you can easily convert to daybook's format.

Let's say your bank exported an example CSV in the following format.

::

    Date, Amount, Description, Category
    10/01/2022,14.56,LOCAL GROCERY STORE,food

This CSV is not compatible with daybook, so we'll convert it.

Create a Python3 script that follows this convention. Lets name it
``convert.py`` for this example.

::

    # Each converter module must have a help, description, headings,
    # and a convert_row function

    # Short description
    help = 'Converter for Mybanks CSVs'

    # Longer, potentially multi-line description.
    description = '''
    Mybank has upcased date and amount fields, and uses a Description heading
    to describe the vendor. This module fixes that.
    '''

    # Headings for CSV.
    headings = 'date,dest,notes,amount'

    # Converter function. Must be called convert_row and accept a single
    # parameter as a dict.
    #
    # The str it returns represents the converted row.
    def convert_row(row):
        date = row['Date']
        dest = row['Description']
        notes = dest
        amount = row['Amount']

        return f'{date},{dest},{notes},{amount}'

To convert this csv we would run ``daybook convert --csvs transactions.csv --converter ./converter.py``
and our output would be...

::

    date,dest,notes,amount
    10/01/2022,LOCAL GROCERY STORE,LOCAL GROCERY STORE,14.56

The order will be the same as in the rules file. Use redirection to save this
output to a file.

::

    daybook convert --csvs transactions.csv --converter ./converter.py > asset.checking.csv

And asset.checking.csv will contain the rows in daybook's format.

While this example is trivial, financial instituions like Schwab and Fidelity
will often do odd things with their CSV exports. Being able to format these rows
using arbitraty python3 scripting is very useful, and allows the scripts to be
reused month after month.

SEE ALSO
========
daybook(1)
