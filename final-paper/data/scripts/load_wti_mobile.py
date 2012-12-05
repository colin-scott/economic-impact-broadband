#!/usr/bin/env python

import sqlite3
import glob
import os
import csv
from canonocalize_names import exact_matches, regexes

conn = sqlite3.connect("../data.sqlite")
conn.text_factory = str  #bugger 8-bit bytestrings
cur = conn.cursor()

def canonicalize_cname(name):
  if name.rstrip() in exact_matches:
    # o(n^2), but i don't care
    return exact_matches[name]

  for regex, replace in regexes.iteritems():
    new = name.replace(regex, replace)
    if new != name:
      return new
  return name

def sanitize_value(v):
  if v is None:
    return None
  try:
    v = v.replace("'", "")
    return float(v)
  except ValueError:
    # Handles "-"
    return None

os.chdir('../WTI/mobile')
for csv_filename in glob.glob("*csv"):
  # Example: 2001_data.csv
  year = int(csv_filename.split("_")[0])
  with open(csv_filename, "rb") as csv_file:
    reader = csv.reader(csv_file, dialect='excel')
    for _, cname, _, _, _, total_mobile, _, _, mobile_per_100, _, _, _, _, _, _, _ in reader:
      (total_mobile, mobile_per_100) = map(sanitize_value,
                                           [total_mobile, mobile_per_100])
      cname = canonicalize_cname(cname)
      cur.execute('''UPDATE wti set total_mobile=?, mobile_per_100=? '''
                  ''' WHERE cname=? AND year=?''',
                  (total_mobile, mobile_per_100, cname, year))

conn.commit()
