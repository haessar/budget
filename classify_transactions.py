"""
Watch remainder of tutorial video for more on custom click decorators, and inherited groups
"""

import calendar

import click

from compile_data import NatWestAccount
from db_setup import Category, Classified
from machine_learning import Predictor
from utils import format_category, tokenizer

REPEAT = 'r'
PASS = 'q'
VALUE = 'v'
LIST = 'l'
PATTERN = 'p'
DATE = 'd'

def correct_category(input, session):
    """
    For given input str and list of categories, determines which category is intended. Considers substrings of
    increasing length, and matches both start of category and within category.
    """
    query = session.query(Category)
    num_category = query.filter(Category.id == input).all()
    if len(num_category) == 1:
        return num_category[0]
    elif not num_category:
        str_category = query.filter(Category.level_one == input).all()
        if len(str_category) == 1:
            return str_category[0]
        for idx in range(len(str(input))):
            substr = str(input)[0:idx+3]
            starts = query.filter(Category.level_one.startswith(substr)).all()
            within = query.filter(Category.level_one.contains(substr)).all()
            if len(starts) == 1 and starts == within:
                return starts[0]
            elif len(starts) == 0 and len(within) == 0:
                raise ValueError('Input category "%s" not recognised.' % input)
        if len(starts) == 0 and len(within) == 1:
            return within[0]
        else:
            raise ValueError('Narrow down category to one of:\n%s' % '\n'.join([cat.level_one for cat in within]))
    elif len(num_category) > 1:
        raise ValueError('Multiple categories were found for category id %s. Rebuild Category table of db.' % input)

class Classifier(NatWestAccount, Predictor):
    counter = 0
    def __enter__(self):
        super(Classifier, self).__enter__()
        self.training_set = self.session.query(Classified)
        self.cats = self.session.query(Category)
        return self
    def classify(self, id, category):
        try:
            classified = Classified(transactions_id=id, category=category.level_one)
            self.session.add(classified)
            self.session.commit()
            self.counter += 1
            click.echo('Classified transaction successfully.')
        except Exception as e:
            click.echo(e)
            self.session.rollback()
    def unique_values(self):
        return sorted({x for v in self.training_set.itervalues() for x in v})
    def list_categories(self):
        return '\n'.join([str(cat.id) + ' : ' + format_category(cat.level_one) for cat in self.cats])

@click.command()
@click.option('--trans', default=10, type=int, help='Number of transactions to display.')
@click.option('--random', default=False, type=bool, help='Take random selection of transactions from db.')
@click.option('--latest', default=False, type=bool, help='Run through transactions from latest to oldest (default is the reverse).')
def classify(trans, random, latest):
    """
    Interface for classifying database transactions.
    """
    with Classifier('debit') as store:
        idx = 0
        data = store.qry.all()
        while store.counter < trans and idx < len(data):
            desc = data[idx].description
            trans_id = data[idx].id
            if not store.training_set.filter_by(transactions_id=trans_id).all():
                while True:
                    click.echo(desc)
                    value = ''
                    while value in ['', REPEAT, VALUE, LIST, DATE]:
                        value = click.prompt(
                            'Please classify this transaction (%s: repeat, %s: pass, %s: value, %s: list categories, %s: pattern match, %s: date)' % (
                                repr(REPEAT), repr(PASS), repr(VALUE), repr(LIST), repr(PATTERN), repr(DATE)
                            ),
                            type=str
                        )
                        if value == REPEAT:
                            click.echo(desc)
                        elif value == VALUE:
                            click.echo('value: ' + str(abs(data[idx].value)))
                        elif value == LIST:
                            click.echo(store.list_categories())
                        elif value == DATE:
                            date = data[idx].date
                            click.echo('date: ' + str(date) + ' ' + str(calendar.day_name[date.weekday()]))
                    else:
                        if value == PATTERN:
                            click.echo('Which pattern would you like to associate with a category?')
                            patterns = tokenizer(desc)
                            index = click.prompt(
                                ', '.join(['%d: %s' % (x, y) for (x, y) in zip(range(len(patterns)), patterns)]),
                                type=int
                            )
                            pattern = patterns[index]
                            while value in [PATTERN, LIST]:
                                # TODO Fix pattern matcher (currently not doing anything with pattern being matched).
                                value = click.prompt(
                                    'Which category would you like to assign "%s" pattern to? (%s: pass, %s: list categories)' % (
                                        pattern, repr(PASS), repr(LIST)
                                    ),
                                    type=str
                                )
                                if value == LIST:
                                    click.echo(str(store.cats))
                        if value == PASS:
                            click.echo('Passed transaction.')
                            break
                        try:
                            corrected_value = correct_category(value, session=store.session)
                            if unicode(corrected_value.id) != value and corrected_value.level_one != value:
                                confirm = click.prompt('Did you mean "%s"? (y/n)' % corrected_value.level_one, type=str)
                                if confirm.lower().startswith('y'):
                                    store.classify(trans_id, corrected_value)
                                    break
                                elif confirm.lower().startswith('n'):
                                    continue
                            else:
                                store.classify(trans_id, corrected_value)
                                break
                        except ValueError as e:
                            click.echo(e)
            idx += 1
        click.echo('No more transactions to classify.')
        # TODO Fix ML predictor
        # store.predict()

if __name__ == '__main__':
    classify.params[0].default = 1
    classify()
