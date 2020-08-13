# -*- coding: utf-8 -*-
from main import import_investec_transactions
import dateutil.parser
import datetime
import sys

if __name__ == "__main__":
    # get the dates to import. defaults to the last 180 days
    now = datetime.datetime.now()
    from_date = now - datetime.timedelta(days=180)
    to_date = now
    args = sys.argv
    if len(args) > 1:
        from_date = dateutil.parser.isoparse(args[1])
    if len(args) > 2:
        to_date = dateutil.parser.isoparse(args[2])
    # Import the transactions
    print("Importing transactions from %s to %s" % (from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")))
    total = import_investec_transactions(from_date, to_date)
    print("Done importing %d transactions" % total)
