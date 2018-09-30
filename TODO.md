# TODO

### FIXES
* NatWest has had website facelift, so selenium_download requires a fix.

### TASKS
1. ~~Create database with all transaction data.~~
2. ~~Iterate through transactions and categorise. (link to transclick)~~
3. Expand the sklearn machine learning stuff in classify_transactions:
    - ~~'y_train' (essentially categories) should be my budget categories.~~
    - ~~Each 'train_set' string is expanded whenever I manually categorise a transaction using transclick.~~
    - ~~Populate 'vocab' using tokens from each transaction that's passed through.~~
    - Investigate changes in ngram_range and alpha arguments for CountVectorizer and MultinomialNB, respectively.
    - ~~Wrap all in class structure.~~
    - Get tips from Vlad's markup_texts code to see why it's not working.
    - Expand train_set to at least 100 examples before testing.
4. ~~Convert update_db from pickle to sqlite3, with ORM using SQLAlchemy.~~
5. ~~Convert db for classify_transactions and compile_data from pickle to db.sqlite3.~~
6. Add comprehensive collection of categories to budgets, as well as corresponding budgetary constraints.
7. Run through classify_transactions to start populating the classified table in db.
8. Set up regular scheduled runs of selenium_download/update_db combo.
9. Read up about cross-referencing parent/child sqlite tables.
10. Write code to generate monthly Excel spreadsheets detailing over/under spend per
 category.
    - Take inspiration from the likes of YNAB for layout.
11. Code for generating some standard visualisations of this data (pie/bar/time series).
    - Take inspiration from Life Cycle app and their doughnuts.
12. Create email client to send regular reports and summaries of spending habits.

### BONUS
* Add further metadata to db tables so that all transactions csvs that have not been
 processed yet are, rather than just taking latest one.
* For pattern matching in classify_transactions, add another table to db called Patterns, with Classified as a parent.
 This can be used as the training set for the prediction algorithm. 