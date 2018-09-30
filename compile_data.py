from update_transactions import Transactions, format_datetime
from natwest_data import accounts
from db_setup import DbSession
from utils import remove_apostrophe

def acc_split(acc_str):
    if '-' in acc_str:
        return acc_str.split('-')
    else:
        return ['', acc_str]

class NatWestAccount(DbSession):
    def __init__(self, type=None):
        self.type = type
    def __enter__(self):
        super(NatWestAccount, self).__enter__()
        self.qry = self.session.query(Transactions)
        if self.type is not None:
            account_data = accounts[self.type]
            self.name = account_data['name']
            self.overdraft = account_data['overdraft']
            self.qry = self.qry.filter_by(account_name=self.name)
            acc = self.qry.distinct().first().account_number
            self.sort_code, self.account_number = acc_split(remove_apostrophe(acc))
        return self
    def transactions(self, *args, **kwargs):
        if len(args) > 0 or kwargs.get('start', ''):
            from_date = kwargs.get('start', '') if kwargs.get('start', '') else args[0]
            date_filter = self.qry.filter(Transactions.date >= format_datetime(from_date))
            if len(args) > 1 or kwargs.get('end', ''):
                end_date = kwargs.get('end', '') if kwargs.get('end', '') else args[1]
                date_filter = date_filter.filter(Transactions.date < format_datetime(end_date))
        return date_filter

if __name__ == '__main__':
    with NatWestAccount('debit') as nw:
        trans = nw.transactions(start='01/07/2017', end='01/08/2017')
        for tran in trans:
            print tran.date
