help = 'Conversion module for USAA checking, savings, and credit cards.'


description = '''
Here is an example USAA checking CSV

Date,Description,Original Description,Category,Amount,Status
2023-07-21,"Mr Bobs Auto","MR BOBS AUTO SHOP",Auto,-33.69,Posted
'''


headings = 'date,dest,notes,amount'


def convert_row(row):

    date = row['Date']
    dest = row['Original Description']
    notes = row['Description']
    amount = row['Amount']

    return f'{date},{dest},{notes},{amount}'
