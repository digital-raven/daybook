help = 'Conversion module for schwab checking.'


description = '''
Here is an example Schwab checking CSV

"Date","Type","Check #","Description","Withdrawal (-)","Deposit (+)","RunningBalance"
"01/17/2023","TRANSFER","","Funds Transfer","$5,000.00","","$0.00"
"01/17/2023","ACH","","TRANSFER FROM SOME BANK","","$5,000.00","$5,000.00"
'''


headings = 'date,dest,notes,amount'


def convert_row(row):
    date = row['Date']

    withdrawal = row['Withdrawal (-)']
    withdrawal = f'-{withdrawal}' if withdrawal else ''
    deposit = row['Deposit (+)']

    amount = withdrawal or deposit

    dest = row['Description']
    notes = row['Description']

    # Remove $ and , from amount
    amount = amount.replace(',', '').replace('$', '')

    return f'{date},{dest},{notes},{amount}'
