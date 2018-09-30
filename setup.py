# Run 'pip install --editable . ' from root directory to install.

from setuptools import setup

setup(
    name='BudgetCLI',
    version='1.0',
    py_modules=['cli'],
    install_requires=[
        'Click',
    ],
    entry_points='''
    [console_scripts]
    budgetcli=cli:cli
    ''',
)
