#!/usr/bin/env python

import sqlite3
import glob
import os
import csv

conn = sqlite3.connect("../data.sqlite")
conn.text_factory = str  #bugger 8-bit bytestrings
cur = conn.cursor()

def sanitize_value(v):
  if v is None:
    return None
  try:
    return float(v)
  except ValueError:
    return None

os.chdir('../WTI/')
for csv_filename in glob.glob("*csv"):
  # Example: 2001_data.csv
  year = int(csv_filename.split("_")[0])
  with open(csv_filename, "rb") as csv_file:
    reader = csv.reader(csv_file, dialect='excel')
    for _, cname, total_inet, _, inet_per_100, _, inet_percent, _, total_broadband, \
            _, broadband_per_100, _, _, _ in reader:
      (total_inet, inet_per_100, inet_percent, total_broadband,
       broadband_per_100) = map(sanitize_value,
                                [total_inet, inet_per_100, inet_percent,
                                 total_broadband, broadband_per_100])
      cur.execute('''INSERT INTO wti VALUES (?,?,?,?,?,?,?)''',
                  (cname, year, total_inet, inet_per_100, inet_percent, total_broadband,
                   broadband_per_100))

conn.commit()
