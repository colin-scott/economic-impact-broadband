#!/usr/bin/env python

import os
import glob
import database
import collections

def get_classifications():
  os.chdir('../country-classifications/')
  cname2classes = collections.defaultdict(list)
  for filename in glob.glob("*"):
    print "filename", filename
    classification = filename
    with open(filename) as file:
      for line in file:
        cname = line.rstrip()
        cname2classes[cname].append(classification)
  return cname2classes

def load_classifications(db, cname2classes):
  for cname, classes in cname2classes.iteritems():
    for classificication in classes:
      db.insert_country_classification(cname, classificication)

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
    cname2classes = get_classifications()
    load_classifications(db, cname2classes)
  finally:
    if db:
      db.close()

