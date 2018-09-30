"""
Monthly budgets for various essential and luxury categories
"""

import itertools

import click
from sqlalchemy import and_

from classify_transactions import correct_category
from db_setup import Budget, Category, DbSession, Income

class Budgeter(DbSession):
    def __enter__(self):
        super(Budgeter, self).__enter__()
        self.qry = self.session.query(Budget)
        total_income = sum(itertools.chain.from_iterable(self.session.query(Income.monthly)))
        total_budget = sum(filter(None, itertools.chain.from_iterable(self.session.query(Budget.monthly))))
        total_yearly = sum(filter(None, itertools.chain.from_iterable(self.session.query(Budget.yearly))))
        self.total_remaining = total_income - total_budget - (total_yearly / 12)
        return self
    def get_or_create(self, model, **kwargs):
        instance = self.session.query(model).filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = model(**kwargs)
            self.session.add(instance)
            self.session.commit()
            return instance
    def assign_budget(self, category):
        filter = self.qry.filter(Budget.category == category).one()
        click.echo('Monthly allocated budget: %s' % filter.monthly)
        click.echo('Total remaining budget: %s' % self.total_remaining)
        monthly = click.prompt('Assign monthly budget: (leave blank if None)', default='', show_default=False)
        if monthly:
            try:
                filter.monthly = float(monthly)
                self.total_remaining -= float(monthly)
                self.session.commit()
                return
            except Exception as e:
                raise e
        click.echo('Yearly allocated budget: %s' % filter.yearly)
        click.echo('Total remaining budget: %s' % (self.total_remaining * 12))
        yearly = click.prompt('Assign yearly budget: (leave blank if None)', default='', show_default=False)
        if yearly:
            try:
                filter.yearly = float(yearly)
                self.total_remaining -= float(yearly) / 12
                self.session.commit()
            except Exception as e:
                raise e

@click.command()
@click.option('--update', is_flag=True, help='Update budget table with latest categories in db.')
@click.option('--assign', type=str, default='all', help='Assign budget to named category.')
def budget(update, assign):
    """
    Interface for amending budget allocations.
    """
    with Budgeter() as db:
        if update:
            categories = db.session.query(Category.level_one).distinct()
            for category in categories:
                db.get_or_create(Budget, category=category.level_one)
            budgets = db.qry.values(Budget.category)
            categories = set(itertools.chain.from_iterable(categories))
            budgets = set(itertools.chain.from_iterable(budgets))
            missing_categories = budgets.difference(categories)
            if missing_categories:
                click.echo('More budgets have been allocated than there are categories in the db.')
                response = click.prompt(
                    ' Would you like to remove\n\t%s\n from budget table? (y/n)'
                    % '\n\t'.join(missing_categories)
                )
                if response.lower().startswith('y'):
                    for missing in missing_categories:
                        to_remove = db.qry.filter(Budget.category == missing).one()
                        db.session.delete(to_remove)
                    db.session.commit()
            click.echo('All categories are up-to-date in budget table.')
        if assign == 'all':
            unassigned = db.qry.filter(and_(Budget.monthly == None, Budget.yearly == None))
            for assignee in unassigned:
                click.echo('--> ' + assignee.category)
                db.assign_budget(assignee.category)
        elif assign:
            corrected_value = correct_category(assign, session=db.session)
            confirm = click.prompt('Did you mean "%s"? (y/n)' % corrected_value.level_one, type=str)
            if confirm.lower().startswith('y'):
                category = corrected_value.level_one
                db.assign_budget(category)
            elif confirm.lower().startswith('n'):
                click.echo('Please ensure category %s is contained in db.' % assign)
        click.echo('Total remaining budget: %s' % db.total_remaining)

if __name__ == '__main__':
    budget()
