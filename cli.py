import click

from classify_transactions import classify
from budgets import budget

@click.group()
def cli():
    pass

cli.add_command(classify)
cli.add_command(budget)