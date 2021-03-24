===========
 Changelog
===========
All notable changes to daybook will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

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
