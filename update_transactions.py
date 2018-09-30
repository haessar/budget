import argparse
import csv
import os

from natwest_data import accounts
from config import transactions_dir
from db_setup import DbSession, Debit, Credit, Isa, Bills, Transactions, Base
from utils import format_datetime, format_header

def latest_transactions(path, file_stub, session):
    files = []
    for fname in os.listdir(path):
        if fname.startswith(file_stub):
            files.append(fname)
    file = sorted(files)[-1]  # Pick most recent file
    with open(os.path.join(path, file)) as f:
        r = csv.reader(f)
        header = []
        data = []
        for row in r:
            if row and not header:
                header = [format_header(item) for item in row if item]
            elif row and header:
                data.append(row)
    try:
        for i in data:
            row = {
                'date': format_datetime(i[0]),
                'type': i[1],
                'description': i[2],
                'value': i[3] if i[3] else float(0),
                'balance': i[4] if i[4] else float(0),
                'account_name': i[5],
                'account_number': i[6]
            }
            account = [acc for acc, vals in accounts.iteritems() if row['account_name'] in vals['name']]
            if len(account) == 1:
                if account[0] == 'debit':
                    table = Debit
                elif account[0] == 'credit':
                    table = Credit
                elif account[0] == 'isa':
                    table = Isa
                elif account[0] == 'bills':
                    table = Bills
                if not [column.key for column in table.__table__.columns] == ['id'] + header:
                    raise ValueError('Column names of table %s and transactions csv file do not match.' % table)
                record = table(**row)
                record_all = Transactions(**row)
                # Avoid adding duplicates
                if not session.query(table).filter(table.date == row['date']). \
                        filter(table.description == row['description']). \
                        filter(table.value == row['value']). \
                        first():
                    session.add(record)
                    session.add(record_all)
            else:
                raise ValueError('Could not detect account for row %s' % row)
        session.commit()
    except Exception as e:
        print e
        session.rollback()  # Rollback the changes on error

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--fresh", help="add transactions tables to db from scratch", action='store_true')
    args = parser.parse_args()
    path = transactions_dir
    file_stub = 'NatWest-download'
    with DbSession() as db:
        if args.fresh:
            Debit.__table__.drop(db.engine)
            Credit.__table__.drop(db.engine)
            Isa.__table__.drop(db.engine)
            Bills.__table__.drop(db.engine)
            Transactions.__table__.drop(db.engine)
            Base.metadata.create_all(db.engine, checkfirst=True)
        latest_transactions(path, file_stub, db.session)
