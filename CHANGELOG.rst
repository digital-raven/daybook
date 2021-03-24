===========
 Changelog
===========
All notable changes to daybook will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[1.0.0-alpha] - 2021-03-24
==========================
There are several feature additions and behavioral changes from the previous
release. The largest of note is that a running instance of daybookd is no longer
required to generate dumps and reports, and duplicate transaction detection is
much more sophisticated than the previous version.

This release also introduces the "add" and "balance" subcommands, automatic
note generation, and changed the expected format of transactions and account
names in CSV lines.

Added
-----
- New subcommands: "add" and "balance".
- The balance, dump, and expense commands can create their reports from local
  CSVs and no longer require a running daybookd. They will still attempt to
  use a server if the --csvs option was not specified.
- A --hints option which can override any hints file that otherwise would have
  been used.
- Notes will automatically be generated for transactions if no notes were
  provided.
- Options both on the command line and in the configuration file to change
  duplicate detection time range. Transactions from different perspectives
  will be classified as duplicates if their dates are within the number of
  days specified by this setting.

Changed
-------
- Account names are now required to be dot-separated fields where the first
  field indicates the type of the account.
- "amount" field is no longer required in a CSV. If it is absent, then 0 will
  be used. This means fewer fields are required for account creation via an
  "accounts.csv".
- If "src" or "dest" headings are present in a CSV, then each line must specify
  an account for that field.
- dump, expense, and load subcommands now use unified command-line options for
  loading CSVs and filtering transactions.
- The involved src and dest accounts in a transaction will automatically orient
  themselves within the ledger so that dest is always on the receiving end.

Fixed
-----
- Proper duplicate detection. Previously, daybook would omit transactions if
  they had identical dates, src and dest accounts, and amounts. This led to
  equivalent transactions being omitted even if they were stored in the same
  CSV file. To fix this, daybook will now remember the basename of the CSV
  from which each transaction originated, so no 2 CSVs with the same basename
  will be able to report a duplicate transaction. This basename is referred to
  as the "perspective" of a transaction within the code.
- To elaborate on the above behavior, transactions whose perspective is the
  empty string (eg. when read from daybookd) will only be classified as
  duplicates if there is an exact date match with an existing transaction.

Removed
-------
- Accounts can no longer have tags. See the new naming convention.
- "target" heading no longer supported in CSVs.
- The "last currency" behavior. If a currency is missing from a transaction,
  then only the primary currency will be suggested. Good riddance to this
  "helpful" feature.
- "investment" is no longer a valid accout type. Seemed redundant with "asset".

[0.1.0-alpha] - 2020-02-09
==========================
First official tag of daybook. This version requires a running instance of
daybookd to load and dump transactions.

Added
-----
- daybook client which can load transactions from a csv to a server, then
  read the transactions back out later for creating reports.
- daybookd server which can hold transactions for clients to read back later.
- clear, dump, expense, and load subcommands for the client.
- Transactions can be filtered when read back from the server.
- Hints file can be specified to help daybook guess the correct account name
  that should be used for a transaction.
- Configurable settings in an ini config file. These include the ledger root,
  primary currency, hostname and port of a daybookd server, and default username
  and password for a client.
- Command-line argument completion.
- Packaging script which can create deb, rpm, gz, or pywheel distributions.
- Ledger, Account, Amount, Transaction, and Hints objects for reading and
  storing transactions from CSVs and other Ledgers.
