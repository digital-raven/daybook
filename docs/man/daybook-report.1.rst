=================
 daybook-report
=================

----------------
Display a report
----------------

.. include:: _manual-section.rst


SYNOPSIS
========

**daybook** [global-opts] **report** *reporter* [options]

DESCRIPTION
===========
Daybook provides a framework for generating one's own financial reports based
on transactions and budgets. The report subcommand takes care of loading the
transactions and calling the function.

The *reporter* module may be a compatible module found in the locations
specified by the ``DAYBOOK_REPORTERS`` enviornment variable, or it can be
the file path to a custom one.

OPTIONS
=======
These options must be specified after the subcommand.

**-b**, **--budgets** *BUDGET* [*BUDGET*...]
        List of budget files. Multiple budgets may be provided. If more than
        one budget is provided, then the amounts associated with each account
        will be added. See the examples for what these look like.

**-h**, **--help**
        Display a help message and exit.

.. include:: _daybook-csv-opts.rst
.. include:: _daybook-filter-opts.rst

Writing your own reporter module
================================
A reporter module is a single python3 script that has the following attrs.

- help: A short description of the module. Printed with **--list**.
- description: A long description printed with **--description**.
- report(ledger, budget): A function which accepts a Ledger and budget.

To create your own report function, you need to understand the ledger and
budget references. These are pretty simple.

Ledger
------
The Ledger class stores transactions and accounts.

- ledger.accounts: A dictionary of accounts where the key is the name of the
  account and the value is an Account reference.
- ledger.transactions: A list of Transaction references.

Account
~~~~~~~
Accounts track their own transactions and balances of all their currencies.

- account.transactions: A list of transactions involving the account.
- account.balances: A dictionary of balances associated with each currency
  in the account. eg. ``account.balances['usd']``

Transaction
~~~~~~~~~~~
Lines from CSVs read into the ledger are stored as Transaction references.
Each transaction has a date, src account, dest account, Amount reference,
tags, and notes. Money flows from source account to destination account.

- t.date: date or datetime when the transaction took place.
- t.src: Reference to the source Account.
- t.dest: Reference to the destination Account
- t.amount: Amount reference.
- t.tags: Set of tags for the transaction.
- t.notes: Notes for the transaction stored as a str.

These ease common filters
- t.accounts: Names of both accounts as a string.
- t.quantity: Higher absolute value of units of currency exchanged in amount.

Amount
~~~~~~
The Amount class tracks the movement of currency.

- amount.src_currency: String representing the currency given.
- amount.src_amount: Float representing the quantity of currency given.
- amount.dest_currency: String representing the currency received.
- amount.dest_amount: Float representing the quantity of currency received.

If ``src_currency`` and ``dest_currency`` are the same then ``src_amount`` and
``dest_amount`` msut also be the same.

budget
------
This is a simple dictionary where the keys are account names and the values are
floats representing how much money each should have.

Budgets are loaded from files which begin with a yaml data block. These files
may be in any format as long as this block is present. The budget may be under
a "budget" key within the yaml, but if that isn't present then the whole block
will be considered the budget. Here's an example in a markdown file.

::

        ---
        budget:
          income.myjob: -5000
          expense.grocery: 300
          liability.mortgage: 1000
          expense.computer: 1500
        ---

    ## Notes
    I've decided to spend 1500 on a gaming PC this month.


EXAMPLES
========
Here is a simple report example, but remember that the report function is
stock python3. Anything you can do in python3 you can do here. Your reports
may be as simple, or complex, as you wish. The only hard and fast rules are
the presence of ``help`` and ``description`` strings and a ``report`` function
that accepts a ledger and budget reference.

::

    # ./expense.py, but this file can be named whatever you want.

    help = 'A simple expense report.'

    description = '''
    This report tallies all dollars spent on expense accounts for
    the supplied transactions.
    '''

    # Report function. Must be called "report" and accept a ledger
    # and budget reference.
    def report(ledger, budget):
        expenses = sum([x.balances['usd'] for x in ledger.accounts if 'expense' in x.name else 0])

        return f'You spent ${expenses} this month.'

And then we would use this report with ``daybook report --csvs ./mycsvs/ --reporter ./expense.py``

SEE ALSO
========
daybook(1)
