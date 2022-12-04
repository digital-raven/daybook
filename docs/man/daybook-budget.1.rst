=================
 daybook-budget
=================

-----------------------------
Show a budget and differences 
-----------------------------

.. include:: _manual-section.rst

SYNOPSIS
========

**daybook** [global-opts] **budget** [options]

DESCRIPTION
===========
This command prints a basic budget report to stdout. It accepts a list
of budgets CSVs and transactions and prints a report about how the
transactions stacked up to the budget.

OPTIONS
=======
These options must be specified after the subcommand.

**-b** *BUDGET* [*BUDGET* ...]
        List of budget files. Multiple budgets may be provided. If more than
        one budget is provided, then the amounts associated with each account
        will be added. See the examples for what these look like.

**-h**, **--help**
        Display a help message and exit.
          -b BUDGETS [BUDGETS ...], --budgets BUDGETS [BUDGETS ...]
                        List of budget files.

.. include:: _daybook-csv-opts.rst
.. include:: _daybook-server-opts.rst
.. include:: _daybook-filter-opts.rst

EXAMPLES
========
Here's an example budget file.

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


SEE ALSO
========
daybook(1)
