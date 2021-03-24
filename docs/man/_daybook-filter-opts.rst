FILTER OPTIONS
--------------
Options for filtering output in commands.

**--start** *DATE*
        Filter for transactions after a date.

**--end** *DATE*
        Filter for transactions before a date.

**--range** *RANGE*
        Provide this with --start to filter within a date range. Can be
        human-readable. eg. "1 month", or "2 weeks"

**--accounts** *NAME* [*NAME* ...]
        Filter for transactions involving the specified account names.

**--currencies** *CURRENCY* [*CURRENCY* ...]
        Filter for transactions involving certain currencies.

**--types** *TYPE* [*TYPE* ...]
        Filter for transactions that involved an account of the matching type.
        Valid entries are "asset", "expense", "income", "liability",
        "receivable", and "void".

**--tags** *TAGS*
        Filter for transactions that involve specific tags. These should be
        provided as a single colon-separated string.
