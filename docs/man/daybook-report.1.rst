=================
 daybook-report
=================

----------------
Display a report
----------------

.. include:: _manual-section.rst


SYNOPSIS
========

**daybook** [global-opts] **report** [options]

DESCRIPTION
===========
Daybook provides a framework for generating your own financial reports based
on your transactions and budgets. This command can point at 

Writing your own report function
================================
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

- self.date: datetime when the transaction took place.
- self.src: Reference to the source Account.
- self.dest: Reference to the destination Account
- self.amount: Amount reference.
- self.tags: Set of tags for the transaction.
- self.notes: Notes for the transaction stored as a str.

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

EXAMPLES
========
Here are some simple example report functions, but remember that the report
function is stock python3. Anything you can do in python3 you can do here. Your
reports may be as simple, or complex, as you wish.

::

    # report.py, but this file can be named whatever you want.

    # Report function. Must be called "report" and accept a ledger
    # and budget reference.
    def report(ledger, budget):
        expenses = sum([x.balances['usd'] for x in ledger.accounts if 'expense' in x.name else 0])

        return f'You spent ${expenses} this month.'


    # This one prints income minus expenses.
    def report(ledger, budget):
        income = sum([x.balances['usd'] for x in ledger.accounts if 'income' in x.name else 0])
        expenses = sum([x.balances['usd'] for x in ledger.accounts if 'expenses' in x.name else 0])

        # income accounts have negative balances and expenses have positives.
        return f'You made ${-income - expenses}'


    # Print balances of transactions involving a particular stock.
    def report(ledger, budget):
        stock_balances = sum(x.balances['SAP500'] for x in ledger.accounts if 'SAP500' in x.balances else 0])

        return f'You own {stock_balances} shares of SAP500'


OPTIONS
=======
These options must be specified after the subcommand.

**--csvs** *CSV* [*CSV*...]
        List of CSV files to load transactions from.

**-b**, **--budgets** *BUDGET* [*BUDGET*...]
        List of files to load a budget from. See the examples for what
        one of these needs to look like.

**--reporter** *reporter.py*
        Path to reporter python3 script. See above for examples.

**-h**, **--help**
        Display a help message and exit.

SEE ALSO
========
daybook(1)
