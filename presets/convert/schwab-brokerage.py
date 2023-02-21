help = 'Convert schwab brokerage accounts.'


description = '''
Here is an example Schwab brokerage CSV.

"Date","Action","Symbol","Description","Quantity","Price","Fees & Comm","Amount"
"01/17/2023","Buy","SWPPX","SCHWAB S&P 500 INDEX","100.000","$50.00","","-$5000.00"
"01/17/2023","Journal","","TRANSFER FUNDS FROM SCHWAB BANK - XXXXXXXXXXXX","","","","$5000.00"
'''


headings = 'date,dest,notes,amount'


def convert_row(row):
    date = row['Date']

    dest = row['Description']
    notes = row['Description']

    action = row['Action']
    if action in ['Buy']:
        dest = 'this'

    # Remove $ and , from amount
    amount = row['Amount']
    amount = amount.replace(',', '').replace('$', '')

    symbol = row['Symbol']
    quantity = row['Quantity']
    if symbol:
        amount = f'{amount}:usd {symbol}:{quantity}'

    return f'{date},{dest},{notes},{amount}'
