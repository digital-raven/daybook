from prettytable import PrettyTable


help = 'Total balance report.'


description = '''
Tally the balances of all accounts.
'''


def report(ledger, budget):
    """ Create a total balance report.
    """
    pt = PrettyTable()
    pt.field_names = ['Account', 'Balance']
    pt.align['Account'] = 'l'
    pt.align['Balance'] = 'r'
    for name in sorted(ledger.accounts):
        account = ledger.accounts[name]
        balances = []
        for cur in sorted(account.balances):
            balance = account.balances[cur]
            balances.append('{}: {}'.format(cur, round(balance, 2)))

        pt.add_row([name, '\n'.join(balances)])

    return str(pt) + '\n'
