#!/usr/bin/env python

import os
import glob
import database

def get_classifications():
  os.chdir('../country-classifications/')
  cname2class = {}
  for filename in glob.glob("*"):
    classification = filename
    with open(filename) as file:
      for line in file:
        cname = line.rstrip()
        cname2class[cname] = classification
  return cname2class

def load_classifications(db, cname2class):
  for cname, classification in cname2class.iteritems():
    db.insert_country_classification(cname, classification)

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
    cname2class = get_classifications()
    load_classifications(db, cname2class)
  finally:
    if db:
      db.close()

