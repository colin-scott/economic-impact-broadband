#!/usr/bin/env python

import sqlite3 as lite
import glob
import os
import time
import calendar
import shutil
import csv
import StringIO
import collections

# `cname' <-> `country name'
# `ccode' <-> `country code'

WTDNAME2CODE = {
  "GDP" : "NY.GDP.PCAP.PP.CD",
  "Investment Share (% of GDP)" : "NE.GDI.TOTL.ZS",
  "Primary school enrollment rate" : "SE.PRM.ENRR",
  "Secondary school enrollment rate" : "SE.SEC.NENR",
}

WTINAME2COLUMN = {
  # TODO(cs): Internet subscriptions a superset of broadband? Or just dialup?
  "1000s of fixed Internet subscriptions" : "total_inet",
  "Internet subscriptions per 100 inhab." : "inet_per_100",
  "% individuals using Internet" : "inet_percent",
  "1000s of fixed broadband subscriptions" : "total_broadband",
  "Broadband subscripts per 100 inhab." : "broadband_per_100",
}

class Database(object):
  def __init__(self, database_file='grades.sqlite'):
    self.con = lite.connect(database_file)
    self.prepare_db()

  def prepare_db(self):
    cur = self.con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS wdi (cname TEXT, ccode TEXT, iname TEXT, icode TEXT, y1960'''
                '''INTEGER,y1961 INTEGER,y1962 INTEGER,y1963 INTEGER,y1964 INTEGER,y1965'''
                '''INTEGER,y1966 INTEGER,y1967 INTEGER,y1968 INTEGER,y1969 INTEGER,y1970'''
                '''INTEGER,y1971 INTEGER,y1972 INTEGER,y1973 INTEGER,y1974 INTEGER,y1975'''
                '''INTEGER,y1976 INTEGER,y1977 INTEGER,y1978 INTEGER,y1979 INTEGER,y1980'''
                '''INTEGER,y1981 INTEGER,y1982 INTEGER,y1983 INTEGER,y1984 INTEGER,y1985'''
                '''INTEGER,y1986 INTEGER,y1987 INTEGER,y1988 INTEGER,y1989 INTEGER,y1990'''
                '''INTEGER,y1991 INTEGER,y1992 INTEGER,y1993 INTEGER,y1994 INTEGER,y1995'''
                '''INTEGER,y1996 INTEGER,y1997 INTEGER,y1998 INTEGER,y1999 INTEGER,y2000'''
                '''INTEGER,y2001 INTEGER,y2002 INTEGER,y2003 INTEGER,y2004 INTEGER,y2005'''
                '''INTEGER,y2006 INTEGER,y2007 INTEGER,y2008 INTEGER,y2009 INTEGER,y2010'''
                '''INTEGER,y2011 INTEGER,y2012 INTEGER,'''
                '''primary key (cname, ccode, iname, icode))''')
    cur.execute('''CREATE TABLE IF NOT EXISTS wti (cname TEXT, year INTEGER, total_inet'''
                ''' REAL, inet_per_100 REAL, inet_percent REAL, total_broadband REAL, '''
                ''' broadband_per_100 REAL, mobile_per_100 REAL, '''
                ''' total_mobile REAL, primary key (cname, year))''')
    cur.execute('''CREATE TABLE IF NOT EXISTS country_classifications '''
                ''' (cname TEXT, class TEXT, primary key (cname, class))''')
    cur.execute('''CREATE TABLE IF NOT EXISTS countries_to_use '''
                ''' (cname TEXT, primary key (cname))''')
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

  def select_cname2classes(self):
    cur = self.con.cursor()
    rows = cur.execute('''SELECT cname, class from country_classifications ''')
    cname2classes = collections.defaultdict(list)
    for row in rows:
      (cname, classification) = row
      cname2classes[cname].append(classification)
    return cname2classes

  def select_class2cnames(self):
    cur = self.con.cursor()
    rows = cur.execute('''SELECT cname, class from country_classifications ''')
    class2cnames = collections.defaultdict(list)
    for row in rows:
      (cname, classification) = row
      class2cnames[classification].append(cname)
    return class2cnames

  def select_wdi_stats(self, code):
    cur = self.con.cursor()
    rows = cur.execute('''SELECT cname,y1960,y1961,y1962,'''
                       '''y1963,y1964,y1965,y1966,'''
                       '''y1967,y1968,y1969,y1970,'''
                       '''y1971,y1972,y1973,y1974,'''
                       '''y1975,y1976,y1977,y1978,'''
                       '''y1979,y1980,y1981,y1982,'''
                       '''y1983,y1984,y1985,y1986,'''
                       '''y1987,y1988,y1989,y1990,'''
                       '''y1991,y1992,y1993,y1994,'''
                       '''y1995,y1996,y1997,y1998,'''
                       '''y1999,y2000,y2001,y2002,'''
                       '''y2003,y2004,y2005,y2006,'''
                       '''y2007,y2008,y2009,y2010,'''
                       '''y2011,y2012 from wdi '''
                       ''' WHERE icode=? '''
                       ''' AND cname in (SELECT * from countries_to_use) '''
                       ''' ORDER BY cname''', (code,))
    tuples = []
    for row in rows:
      (cname,y1960,y1961,y1962,y1963,y1964,y1965,y1966,y1967,y1968,y1969,y1970,y1971,y1972,y1973,y1974,y1975,y1976,y1977,y1978,y1979,y1980,y1981,y1982,y1983,y1984,y1985,y1986,y1987,y1988,y1989,y1990,y1991,y1992,y1993,y1994,y1995,y1996,y1997,y1998,y1999,y2000,y2001,y2002,y2003,y2004,y2005,y2006,y2007,y2008,y2009,y2010,y2011,y2012) = row
      # Super awkward. Should have one row per year instead.
      # Also makes it awkward to select on WHERE clauses!
      year = 1959
      for data in y1960,y1961,y1962,y1963,y1964,y1965,y1966,y1967,y1968,y1969,y1970,y1971,y1972,y1973,y1974,y1975,y1976,y1977,y1978,y1979,y1980,y1981,y1982,y1983,y1984,y1985,y1986,y1987,y1988,y1989,y1990,y1991,y1992,y1993,y1994,y1995,y1996,y1997,y1998,y1999,y2000,y2001,y2002,y2003,y2004,y2005,y2006,y2007,y2008,y2009,y2010,y2011,y2012:
        year += 1
        if data is None or data == u'':
          continue
        tuples.append((year,cname,data))
    return tuples

  def select_wti_stats(self, column):
    cur = self.con.cursor()
    query = ('''SELECT year, cname, %s FROM wti WHERE %s is not null '''
             ''' AND %s!='' AND cname in (SELECT * FROM countries_to_use) '''
             ''' ORDER BY cname''' % (column, column, column))
    rows = cur.execute(query)
    return list(rows)

  def populate_countries_to_use(self, max_year=2012):
    cur = self.con.cursor()
    # We select countries that have data, and are common to both datasets
    cur.execute('''DELETE FROM countries_to_use''')
    cur.execute('''INSERT OR IGNORE INTO countries_to_use '''
                '''SELECT DISTINCT cname FROM wdi '''
                ''' WHERE y1980!="" AND icode="NY.GDP.MKTP.KD.ZG"'''
                ''' INTERSECT '''
                '''SELECT DISTINCT cname FROM wdi '''
                ''' WHERE y1980!="" AND icode="NY.GDP.PCAP.KD"'''
                ''' INTERSECT '''
                '''SELECT DISTINCT cname FROM wdi '''
                ''' WHERE y1980!="" AND icode="NE.GDI.TOTL.ZS"'''
                ''' INTERSECT '''
                '''SELECT DISTINCT cname FROM wdi '''
                ''' WHERE y1980!="" AND icode="SE.PRM.ENRR"'''
                ''' INTERSECT '''
                '''SELECT DISTINCT cname from wti '''
                ''' WHERE broadband_per_100!='' AND '''
                ''' broadband_per_100 is not null AND '''
                ''' year <= ?''', (max_year))
    self.con.commit()

  def select_countries_to_use(self):
    cur = self.con.cursor()
    rows = cur.execute('''SELECT * FROM countries_to_use ORDER BY cname''')
    return [ row[0] for row in rows ]

  def close(self):
    self.con.close()

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--sqlite-file',
                      default="../data.sqlite", dest="db_file",
                      help='''sqlite grading database file''')
  args = parser.parse_args()

  db = None
  try:
    db = Database(args.db_file)
  finally:
    if db:
      db.close()
