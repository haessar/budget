### Current workflow:
1. Run selenium_download at regular intervals to download latest transactions from NatWest.
2. Each of these runs should be followed by a run of update_transactions to ensure latest
 transactions are added to database.
3. Running the command line tool 'transcli' will iterate through transactions in database
 that have not been categorised yet, and allow user to manually categorise them into one
 of the pre-established budget categories.
    - In future, there will be an element of machine learning to auto categorise
     certain transactions, where possible.

### Future:
4. Generate monthly spreadsheets detailing where certain budget categories have been
 over/under spent.
5. Regular email summaries of spending habits, with graphical display of this data 
 in the form of charts. 