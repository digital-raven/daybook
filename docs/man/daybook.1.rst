=========
 daybook
=========

-----------------------
Command-line accounting
-----------------------

.. include:: _manual-section.rst

SYNOPSIS
========

**daybook** [global-opts] *command* [options]

DESCRIPTION
===========
Daybook is a command-line accounting program. The main use of Daybook is to
load transactions from CSV files for the purpose of creating expense reports,
summaries of account balances, or viewing a comprehensive record of one's
finances. Daybook was designed to help its users conveniently import and
analyze financial history from CSV files they download from their bank.

Each transaction is double-entry and accounts and currencies are created as
they are mentioned. This means that even a single transaction is enough to
constitute a valid ledger.

The following is an example Daybook CSV that specifies all possible fields
and contains a single transaction.

::

    date,src,dest,amount,tags,notes
    1970/01/01,asset.checking,expense.food,-10 usd,fast-food:food,Wendys.

Each transaction has a date, the name of a source account, the name of a
destination account, an amount which can specify different currencies and
amounts exchanged between source and destination accounts, and tags and notes.
The above transaction will debit 10 dollars from the asset.checking account and
credit it to the expense.food account.

Daybook can be quite clever with how transactions are loaded. The real strength
of Daybook is minimizing the amount of manual work required to import
transactions. The **EXAMPLES** section of this man page goes into more detail
with example transactions, use-cases, and information about what each field
expects for its input. Daybook's subcommands use the information in these CSVs
to create useful reports. Each subcommand has its own man page. These are
referenced in the **SEE ALSO** section.

OPTIONS
=======
These global options must be specified before the subcommand.

**--config** *CONFIG*
        Select a custom configuration file.

**--primary-currency** *CURRENCY*
        Override the primary_currency in the configuration file.

**-h, --help**
        Print the help message for Daybook.

CONFIGURATION
=============
This section covers the options in Daybook's configuration file. This file is
in ini format and is installed at ~/.config/daybook/daybook.ini. A custom
configuration file may be specified using a command-line option.

General Options
---------------
General options regarding the interpretation of transactions.

**primary_currency**
        This is the primary currency that Daybook will use if no currency is
        provided for a transaction.

**duplicate_window**
        When reading transactions from CSVs, sometimes two transactions will
        come from CSVs with different basenames (eg. asset.investment.csv vs
        asset.checking.csv). The transactions will be considered duplicates of
        each other if they are identical in src and dest accounts, amounts,
        and whose dates are within *duplicate_window* number of days. If this
        is the case for two transactions, then the second transaction will be
        automatically ignored during loading.

Server Options
--------------
These are for connecting to a daybookd server. This can store transactions
in memory in case repeated operations on CSVs in the filesystem are too slow.
See the daybookd man page for more information.

Do not regard this server as secure or as something that should be hosted
remotely. The plaintext username and password in daybook.ini should be proof
enough of that.

**hostname**
        Hostname where a daybookd server is listening. Defaults to "localhost".

**port**
        Port on which daybookd is listening.

**username**
        Username for the daybookd server. The server will automatically create
        an account for usernames when they load transactions.

**password**
        Password for the username. The daybookd will reject your attempt to
        connect if the password does not match the associated username.

EXAMPLES
========
This section details what inputs are expected for each field of a transaction
and shows examples and use-cases.

Transactions may have the following fields. Some combination of these are
required as the headings for a CSV. The "date" field is the only strictly
necessary field; the rest are optional and will be automatically determined by
Daybook in their absence.

- date: The day and time of the transaction. The best format to use is Y/m/d.
- src: The name of the source account. Daybook will assume the basename of the
  CSV is the account name if this heading is not present.
- dest: The name of the destination account. Same absentee rules as src.
- amount: The amount exchanged in the transaction. This field is quite flexible,
  and the following examples go into more detail.
- tags: Tags may be assigned to a transaction. Tags are separated by colons.
  This heading is optional.
- notes: Any special notes about the transaction. This field will be
  automatically generated if it wasn't provided.

For the rest of this section, any lines that begin with a "#" should be
regarded as comments.

Dates
-----
Year/month/day is the best way to specify dates, but Daybook can also accept
dates formatted as month/day/year, or dates formatted like "March 3 2019" or
"Saturday" (although non-absolute dates are not recommended). Times may also
be specified after the date in the "hour:minute:second" format.

Avoid day/month/year. This format is ambiguous with month/day/year for a large
variety of dates and will only be used if day > 12. This format is likely to
produce astonishing behavior.

Account names and types
-----------------------
All account names must be a dot-separated series of words with no spaces, and
the first field must indicate the account's type. There are 6 valid account
types.

- asset: Accounts that add to one's net worth.
- liability: Indicate debts that subtract from one's net worth.
- income: Represents money paid to you.
- expense: Categories of things one spends money on.
- receivable: Money owed to you.
- void: Utility account type for adding or deleting money from other accounts.
  For example, setting a starting balance on a checking account the day you
  start using Daybook for book-keeping.

If either the src or dest fields are absent from a CSV, then Daybook will use
the basename of the CSV, minus the "csv" extension, as the account's name. If
the following transaction were read from a file named "asset.checking.csv",
then Daybook would associate "asset.checking" with the missing src heading.

::

    date,dest,amount,notes
    1970/01/01,expense.food,-10,"Wendy's"

The other way to get this behavior is by entering "this" for the respective
field. If the word "this" is provided for "src" or "dest" fields, then Daybook
will replace "this" with the basename of the CSV.

General Use
-----------
This section covers the typical case of tracking transactions downloaded from
one's bank account.

A user typically downloads transactions from their bank for a specific account,
like their checking account. This means all transactions in a file like this
should use the checking account as the src account.

Every bank has different formats for their CSV downloads, so almost none of
them will be compliant with Daybook's expected headings. The following example
walks through a typical usage of Daybook.

::

    # Downloaded and renamed to asset.checking.csv
    Date,Vendor,Description,Exchanged
    2020/08/03,BP BEYOND PETROLEUM #1445,BP Beyond Petroleum,-29.47

Since every bank has a different format for their CSVs, we will have to modify
the headings. This is the easiest part of importing transactions; simply modify
the CSV using your favorite spreadsheet program. In the above case, we would
do this as follows.

::

    # Delete the "Description" heading because it's redundant.
    date,dest,amount
    2020/08/03,BP BEYOND PETROLEUM #1445,-29.47

Notice that we didn't add a "src" field. "asset.checking" will automatically be
used as the src account because "asset.checking.csv" is the filename. Any
negative values in the amount field will deduct funds from asset.checking, and
any positive values will credit funds to asset.checking.

We also didn't change the dest account to something like "expense.gas". This is
because a CSV like this example might have over 100 such transactions, and
Daybook was written to minimize manual effort. Daybook can automatically
associate certain patterns in the src or dest fields with specific accounts.

This association is performed using a "hints" file, which assigns patterns
in the src and dest fields to specific accounts. This file is literally named
"hints". In the above case, our hints file might look like this.

::

    # Multiple patterns each on their own line.
    expense.gas =
        BP BEYOND PETROLEUM
        SHELL
        KWIK TRIP
        TIM HORTONS

If Daybook were to use a hints file containing this example assignment, then
any src or dest field containing any of those patterns would automatically use
"expense.gas" as the account name.

This implies the first few uses of Daybook will be a little painful, but will
grow much easier as the user creates a gradually more comprehensive hints file.

When loading transactions, Daybook will automatically associate CSVs and hints
files if they are located in the same directory. If Daybook is recursing down a
directory searching for CSV files and it finds a hints file, then that hints
file will be used with any CSVs that are below it.

A specific hints file may also be specified as a command-line argument, which
will overrule any hints files that would otherwise have been automatically
selected.

CSV Organization
----------------
Some basic file organization will help in one's book keeping. This section
suggests such an organization to the user. Daybook does not require any
specific organization, as CSVs are treated agnostically, but some organization
helps one navigate their own ledger on their own terms.

The following example is the directory layout of a relatively small ledger. The
"cash" directory contains monthly transactions from one's bank, each sorted
into folders by year and month. The "education" contains a CSV for tracking
student loans. The "investments" folder tracks various investments, and the
example brokerage, ROTH, and traditional IRA accounts are downloaded quarterly.
The "loans" folder holds CSVs that track various liabilities.

Note the location of the "hints" file. If a command like `daybook balance
--csvs=./ledger/cash/` is run, then that hints file will automatically be
assigned to all CSVs at or below the cash directory.

::

        ledger/
        ├── cash
        │   ├── 2019
        │   │   ├── 10
        │   │   │   └── asset.checking.csv
        │   │   ├── 11
        │   │   │   └── asset.checking.csv
        │   │   └── 12
        │   │       └── asset.checking.csv
        │   ├── 2020
        │   │   ├── 01
        │   │   │   └── asset.checking.csv
        │   │   └── 02
        │   │       └── asset.checking.csv
        │   └── hints
        ├── education
        │   └── liability.student-loan.csv
        ├── investments
        │   ├── asset.company.401k.csv
        │   └── usbank
        │       └── 2020
        │           ├── q1
        │           │    ├── asset.usbank.brokerage.csv
        │           │    ├── asset.usbank.tradira.csv
        │           │    └── asset.usbank.rothira.csv
        │           └── q2
        │                ├── asset.usbank.brokerage.csv
        │                ├── asset.usbank.tradira.csv
        │                └── asset.usbank.rothira.csv
        └── loans
            ├── liability.2014-toyota-camry.csv
            └── liability.mortgage.csv

Again, this is just an example of how a user may decide to organize their CSVs
on their computer's file system. Daybook does not enforce any specific
organization.

Amounts
-------
The "amount" field is very flexible because Daybook simultaneously balances
convenient data entry while being able to exchange multiple currencies in a
single transaction.

The amount field can accept 1, 2, or 4 values. These values may be separated
by spaces or colons. If 1 value is provided, it must be a numeric entry and
the ledger's primary currency will be assumed. If 2 values are entered, then
it's assumed that one is the name of a specific currency and the other is a
numeric entry specifying how many units of this currency are being exchanged.
If 4 values are entered, then 2 should be the names of currencies, and 2 should
be the number of units being exchanged.

In all cases, the first number and currency are associated with the account in
the "src" field, and the second number and currency are associated with the
"dest" field. If 2 numeric values are provides, then one must be positive and
one must be negative. If the currency for each side of the transaction is the
same, then the values must zero out.

Duplicate Transactions
----------------------
Daybook is quite clever in detecting transactions which are likely duplicates.
This was designed because CSVs can quite often record the same event, but from
different perspectives. A common example involves money transferred between two
accounts. If a user sends money from their checking account to their investment
account, it is possible that the investment account will record the date of the
transaction as one day later than the checking account. If Daybook did not
perform checks for these duplicates, then these would register as 2 separate
transactions, which is not accurate.

If two transactions were loaded from CSVs with different basenames, and they
record the same amount of money moving to and from the same accounts, and these
transactions have dates within a certain day range, and the transactions were
reported from 2 different CSV files, then Daybook will consider the transactions
to be duplicates and only one will be committed to the ledger.

However, if a third "equivalent" transaction has a date within this day range,
but the date is not one of the other 2 already read, then this transaction will
be considered unique. This is because transactions realistically only have
2 possible relevant dates: their "sent" and "received" date. If a third date
is read, then clearly this is a unique event.

Here are some examples of duplicate transactions. Let's say duplicate_window is
set to 5.

::

    # These two will not be duplicates because they are from the same file.
    date,src,dest,amount
    1970/01/01,asset.checking,expense.food,-10
    1970/01/01,asset.checking,expense.food,-10

    # These next two files contain transactions that are duplicates.

    # asset.checking.csv
    date,dest,amount
    1970/01/01,asset.investment,-100

    # asset.investment.csv
    date,dest,amount
    1970/01/06,asset.checking,100

    # This will not count as a dupe because the previous 2 have already been
    # paired for the 1st and 6th of January.

    # some-other-third.csv
    date,src,dest,amount
    1970/01/02,asset.checking,asset.investment,-100

    # This will not count as a dupe because the money is flowing the other way.

    # some-other-fourth.csv
    date,src,dest,amount
    1970/01/06,asset.checking,asset.investment,100

The transactions within asset.checking.csv and asset.investment.csv will count
as duplicates because the same amount of money was sent to and from the same
accounts within a specified day range. The third transaction does not count
as a duplicate because even though the same accounts are involved, a 3rd date
is reported which indicates a separate event. The fourth transaction registers
as a unique transaction because the source and destination accounts are flipped.

Automatic note generation
-------------------------
If no notes are provided, then Daybook will automatically generate them using
the values listed in the CSV. This is done to prevent losing information
when a line like "BP BEYOND PETROLEUM" is transformed into expense.gas. For
example...

::

    # asset.checking.csv
    date,dest,amount
    1970/01/01,MY FAVORITE BAR,-12.00

Let's say an associated hints file transforms "MY FAVORITE BAR" into
"expense.food". The above transaction would be dumped as follows.

::

    "1970-01-01 00:00:00","asset.checking","expense.food","usd:-12.00 usd:12.00","","MY FAVORITE BAR"

This preserves information in the dump about where the transaction took place.

Use Cases
---------
Let's examine some use cases.

1. Basic transaction.

To send money from src to dest, the first value should be negative. If the
primary currency were "usd", the following transaction would move $10 from
asset.checking into expense.food.

::

    date,src,dest,amount
    1970/01/01,asset.checking,expense.food,-10

2. Credit the src account.

The first numeric value in the "amount" field represents the amount of money
the src account gains from the transaction. If this field is negative, then the
src account is losing money. If it's positive, then the src account will be
credited and Daybook will swap the src and dest accounts under the hood.

Let's say you were paid by your employer, or received a refund from a merchant.
The following transaction is an example of how one would credit their checking
account. This transaction will credit the src account because the amount is
positive.

::

    # asset.checking.csv. This will also be the name of the src account
    # because there is no src field.
    date,dest,amount,notes
    1970/01/01,income.employer,2000,"Got my raise!"
    1970/01/01,expense.food,-30,"Blowfish dinner."
    1970/01/01,expense.hospital.er,-400,"Nearly died."
    1970/01/01,expense.food,30,"Refunded due to food poisoning."

3. Other currencies.

Other currencies can be specified, and currencies are created within the Ledger
as they are read from the CSVs. Let's say the primary currency of your ledger
was usd, but your friend gave you 20 pesos (mxn) as a gift. The following
transaction will credit your asset.cash account with 20 pesos from your friend.

::

    date,src,dest,amount
    1970/01/01,asset.cash,income.gifts.friend,20 mxn

The following styles will accomplish the same thing. The numeric values and
currencies may be specified in any order::

    date,src,dest,amount
    1970/01/01,asset.cash,income.friend,20:mxn

    date,src,dest,amount
    1970/01/01,asset.cash,income.friend,mxn 20

    # Swap src and dest accounts
    date,src,dest,amount
    1970/01/01,income.friend,asset.checking,-20 mxn

There is no need to declare "mxn" as a currency anywhere before its use in a
CSV; an entry will automatically be created for it under the associated
account's balances.

4. Purchasing stock.

Stock symbols are just like currencies. Just use their symbol in a transaction.
Let's say the following CSV lines are from a file called asset.investment. It
receives some money from your checking account and then purchases stock within
the account.

::

    # Filename is asset.investment.csv
    date,src,dest,amount,notes
    1970/01/01,this,asset.checking,1000 usd,"Transferred money."
    1970/01/01,this,this,-1000 usd 10 TSLA,"Bought 10 shares of Tesla."

You may also decide to factor out monetary transfers into their own CSV files.
It may make keeping track of stock transfers easier. Remember; the basename
of the CSV will be used for absent src or dest headings.

::

    # File 1: transfers.csv
    date,src,dest,amount,notes
    1970/01/01,asset.investment,asset.checking,1000 usd,"Transferred money."

    # File 2: asset.investment.csv. Fewer headings required.
    date,amount,notes
    1970/01/01,-1000 usd 10 TSLA,"Bought 10 shares of Tesla."

The second of the above transactions will remove $1000 from asset.investment
and credit it with 10 shares of TSLA.

5. Liabilities (loans).

A liability account is one which tracks debt you owe. A liability account
with a negative balance represents money you owe. The following example shows
how one would create a new liability and pay it off.

Let's say you finance a new car for $10,000. First we have to debit a liability
account. There are a couple of ways to do this.

::

    # Could send money into the void.
    date,src,dest,amount
    1970/01/01,liability.car,void.void,-10000

    # Or treat the transaction as an expense directly.
    date,src,dest,amount
    1970/01/01,liability.car,expense.auto,-10000

    # Or credit a checking account and then buy the car.
    date,src,dest,amount
    1970/01/01,liability.car,asset.checking,-10000
    1970/01/01,asset.checking,expense.car,-10000

All of the above examples will leave your ledger with a liability account with
a balance of negative $10,000. Every car payment should go toward this account.

::

    date,src,dest,amount,notes
    1970/01/01,asset.checking,liability.car,-150,"Car payment."

If the bank has a special identifier for a loan payment, it can be easy to
avoid manual entry with a hints file.

But loans have interest, so how do we track it? Some banks will clearly
separate the principal and interest portions of a loan payment. This makes
interest tracking easy. Other banks don't, so interest will have to be
calculated manually. Either way, it can be done in one of two ways.

::

    # Track as you pay.
    date,src,dest,amount,notes
    1970/01/01,asset.checking,liability.car,-120,"Principle"
    1970/01/01,asset.checking,expense.car.interest,-30,"Interest"

    # Debit the loan account directly.
    date,src,dest,amount,notes
    1970/01/01,liability.car,expense.car.interest,-30,"Interest accrued."
    1970/01/01,asset.checking,liability.car,-150,"Paying principle and interest"

    # Imported long after payoff and the division between principle and
    # interest has been lost.
    1970/01/01,liability.car,expense.car,-10000,"Bought new car"
    1970/01/01,liability.car,expense.car.interest,-1500,"All interest on car."
    1970/01/01,asset.checking,liability.car,-150,"Principle"
    1970/02/01,asset.checking,liability.car,-150,"Principle"
    1970/03/01,asset.checking,liability.car,-150,"Principle"
    ...
    1975/01/01,asset.checking,liability.car,-150,"Paid off!"

In the third example, we went "back in time" so to speak, and debited all
interest at once. We did this because the hypothetical user in this example
didn't know how to divide the interest and principle of this old loan because
the records were too old to indicate that.

The reason we debit the interest from the liability in the second and third
cases is because, if we didn't, then the liability would end with a positive
balance, which suggests overpayment. This is not correct because interest
accrued throughout the life of the loan and this interest needs to be either
tracked separately or tied directly to the loan.

6. Receivables.

A receivable account with a positive balance reflects money that is owed to you.

Let's say you spend money on food while on a business trip, and your business
is expected to reimburse you. The following examples show how Daybook can be
used to track the receivables.

::

    # asset.checking.csv
    date,dest,amount,notes
    1970/01/01,receivable.company,-10,"Food at airport. Company should reimburse."
    1970/01/01,receivable.company,-90,"Rental car. Company should reimburse."


When downloading transactions from your bank, manually change the expenses
that should be reimbursed to "receivable.company". Now the receivable.company
account has a positive balance. When the company repays your checking account,
mark it as a credit from the receivable account.

::

    # asset.checking.csv
    date,dest,amount,notes
    1970/01/01,receivable.company,100,"Company reimbursement."

Let's say your company doesn't compensate everything, leaving the receivable
account with a positive balance that you don't care to chase down. You can either
throw the money into void.void or you may send it to an account (eg. Name it
"expense.lost") to track money that you'll never see again.

::

    date,src,dest,amount,notes
    1970/01/01,asset.checking,receivable.company,-10,"Food at airport. Company should reimburse."
    1970/01/01,asset.checking,receivable.company,-90,"Rental car. Company should reimburse."
    1970/01/01,asset.checking,receivable.company,90,"Partial reimbursement. I hate my job."
    1970/01/01,receivable.company,expense.lost,-10,"W/e it's 10 bucks."

Because receivables are specific to one's own life circumstance and are a
special case, there is no automated way to handle them. Some manual entry will
always be required. No software in the world can avoid that.


SEE ALSO
========
daybook-add(1),
daybook-balance(1),
daybook-clear(1),
daybook-dump(1),
daybook-expense(1),
daybook-load(1),
daybookd(1)
