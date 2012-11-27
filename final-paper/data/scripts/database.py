#!/usr/bin/env python

import sqlite3 as lite
import glob
import os
import time
import calendar
import shutil
import csv
import StringIO

# cname <-> country name
# ccode <-> country code

class Database(object):
  def __init__(self, database_file='grades.sqlite'):
    self.con = lite.connect(database_file)
    self.prepare_db()

  def prepare_db(self):
    cur = self.con.cursor()
    # TODO(cs): create table if not exists wti and wdi

    cur.execute('''CREATE TABLE IF NOT EXISTS country_classifications '''
                ''' (cname TEXT, class TEXT)''')
    self.con.commit()

  def get_distinct_wti_cnames(self):
    cur = self.con.cursor()
    rows = cur.execute('''SELECT DISTINCT cname from wti''')
    return map(lambda t: t[0], rows)

  def change_wti_cname(self, old, new):
    cur = self.con.cursor()
    cur.execute('''UPDATE wti SET cname=? WHERE cname=?''',
                (new, old,))
    self.con.commit()

  def insert_country_classification(self, country, classification):
    cur = self.con.cursor()
    cur.execute('''INSERT OR IGNORE INTO country_classifications '''
                ''' (cname, class) VALUES (?,?)''',
                (country, classification,))
    self.con.commit()

  def select_country_classifications(self):
    cur = self.con.cursor()
    rows = cur.execute('''SELECT cname, class from country_classifications ''')
    cname2class = {}
    for row in rows:
      (cname, classification) = row
      cname2class[cname] = classification
    return cname2class

  def close(self):
    self.con.close()

