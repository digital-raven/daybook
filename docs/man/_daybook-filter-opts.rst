FILTER OPTIONS
--------------
Options for filtering output in commands.

**--filter** *filter*
        Provide a python3 conditional expression to filter transactions on.
        Each transaction is referenced by the letter 't'.

        eg. To filter on each transaction after the first of this month.

            --filter "t.date > 'first of last month'"

        Or to see all transactions with "expense" involved in the accounts.

            --filter "'expense' in t.accounts"

        See the documentation for the report subcommand to learn about
        the attributes in a transaction class.
