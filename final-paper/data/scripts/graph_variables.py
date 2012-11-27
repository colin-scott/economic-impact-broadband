#!/usr/bin/env python

import os
import database

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--sqlite-file',
                      default="../data.sqlite", dest="db_file",
                      help='''sqlite grading database file''')
  args = parser.parse_args()

  db = None
  try:
    db = database.Database(args.db_file)
    cname2class = db.select_country_classifications()
    database.WTDNAME2CODE
    database.WTINAME2COLUMN
  finally:
    if db:
      db.close()

