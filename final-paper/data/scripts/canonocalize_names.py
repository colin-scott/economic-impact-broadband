#!/usr/bin/env python

import database

exact_matches = {
  "Virgin Islands (US)" : "Virgin Islands (U.S.)",
  "Turks & Caicos Is." : "Turks and Caicos Islands",
  "TFYR Macedonia": "Macedonia, FYR",
  "Macao, China": "Macao SAR, China",
  "Lao P.D.R": "Lao PDR",
  "Korea (Rep.)": "Korea, Rep.",
  "Iran (I.R.)": "Iran, Islamic Rep.",
  "Hong Kong, China": "Hong Kong SAR, China",
  "Dominican Rep.": "Dominican Republic",
  "D.P.R. Korea": " Korea, Dem. Rep.",
  "Congo (Dem. Rep.)": "Congo, Dem. Rep.",
  "Congo": "Congo, Rep.",
  "Central African Rep.": "Central African Republic",
  "Venezuela": "Venezuela, RB",
}

regexes = {
  ".*&.* ": "and",
}

def canonicalize(db):
  names = db.get_distinct_wti_cnames()
  for name in names:
    if name.rstrip() in exact_matches:
      # O(n^2), but I don't care
      db.change_wti_cname(name, exact_matches[name])

    for regex, replace in regexes.iteritems():
      new = name.replace(regex, replace)
      if new != name:
        db.change_wti_cname(name, new)

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
    canonicalize(db)
  finally:
    if db:
      db.close()

