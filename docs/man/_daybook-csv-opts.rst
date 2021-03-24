CSV OPTIONS
-----------
Options for loading CSVs from the filesystem.

**--csvs** *csv* [*csv* ..]
        List CSV files to load. Directories will be recursively searched
        for CSVs.

**--duplicate-window** *DAYS*
        Day range for duplicate transactions. If 2 transactions from CSVs
        with different basenames have the same src and dest accounts, identical
        amounts, and whose dates are less-than or equal to the number of days
        specified by this argument, then Daybook will determine those
        transactions are duplicates and the second transaction will not be
        committed to the ledger.

**--hints** *hints*
        Specify a hints file to override automatically detected hints files.
