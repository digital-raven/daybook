=============
 daybook-add
=============

----------------------------------------
Interactively add a transaction to a CSV
----------------------------------------

.. include:: _manual-section.rst

SYNOPSIS
========
**daybook** [global-opts] **add** [options] csv

DESCRIPTION
===========
The "add" subcommand assists in manually adding a transaction to a specific
CSV. This addition is done interactively and the command makes effort to assist
with tab auto completion. The CSV file is first parsed for existing accounts and
currencies and these existing entries are used to assist with auto completion.
The CSV file need not be completely valid for this command to work. Invalid
entries will be skipped.

The command will prompt for date, source account, destination account, the
amount, tags, and notes of the transaction. It is perfectly fine to use
relative dates here (eg. "today", "yesterday"...) as Daybook will convert
them to absolute when writing the transaction to the CSV.

ARGUMENTS
=========
*csv*
        Specify the CSV which will append the transaction.

OPTIONS
=======
**--hints** *HINTS*
        Specify a hints file to assist with auto-completion. If not provided,
        then Daybook will attempt to use a hints file in the same directory
        as the CSV.

**-h**, **--help**
        Display a help message and exit.

HEADING OPTIONS
---------------
Use these to pre-fill fields. They will only be used if the respective headings
are present in the CSV.

**--date** *DATE*
        The date on which the transaction took place.

**--src** *SRC*
        Name of the source account.

**--dest** *DEST*
        Name of the destintion account.

**--amount** *AMOUNT*
        The amount and currencies exchanged between accounts.

**--tags** *TAGS*
        Tags for the transaction. Tags are colon-separated words with no spaces.

**--notes** *NOTES*
        Free-form notes on the transaction.

SEE ALSO
========
daybook(1)
