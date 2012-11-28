#!/usr/bin/env python

# TODO(cs): should use matplotlib instead of the template
from gpi_template import template
import os
import sys
sys.path.append("../")
import database
import collections
import scipy

def assign_categories(tuples, cname2class):
  # { (year, class) -> [data1, data2,... ] }
  year_classification2stats = collections.defaultdict(list)
  for year, cname, data in tuples:
    if cname not in cname2class:
      continue
    classification = cname2class[cname]
    year_classification2stats[(year,classification)].append(data)
  return year_classification2stats

def combine_categories(year_classification2stats):
  # upper-middle
  # lower-middle
  # low
  # high
  lower_classes = set(["upper-middle","lower-middle","low"])
  year_agg2stats = collections.defaultdict(list)
  # fold low and middle into one, and fold all into "overall"
  for year_classification, stats in year_classification2stats.iteritems():
    (year, classification) = year_classification
    if classification in lower_classes:
      key = (year,"low&middle")
    else:
      key = (year,"high")
    year_agg2stats[key] += stats

    # Also add to "overall"
    year_agg2stats[(year,"overall")] += stats
  return year_agg2stats

def compute_averages(year_classification2stats):
  # Averages are really only used for the graphs. For the regression, the
  # datapoints are kept in, and instead a separate variable is made for BBNDH and
  # BBNDL
  year2classification2avg = collections.defaultdict(dict)
  for year_classification, stats in year_classification2stats.iteritems():
    (year, classification) = year_classification
    avg = scipy.mean(stats)
    year2classification2avg[year][classification] = avg

  tuples = []
  sorted_years = year2classification2avg.keys()
  sorted_years.sort()
  for year in sorted_years:
    classification2avg = year2classification2avg[year]
    for classification in ["high","low&middle"]:
      if classification not in classification2avg:
        classification2avg[classification] = "NaN"
    # Order of columns: year,high,overall,low&middle
    tuples.append((year,classification2avg["high"],
                        classification2avg["overall"],
                        classification2avg["low&middle"]))
  return tuples

def write_outputs(name, code, tuples):
  (gpi_filename, dat_filename, output_filename) = get_filenames(name, code)
  write_data_file(dat_filename, tuples)
  write_template(gpi_filename, output_filename, name, dat_filename)
  # invoke gnuplot
  os.system("gnuplot %s" % gpi_filename)

def get_filenames(name, code):
  return (code + ".gpi", code + ".dat", code + ".pdf")

def write_data_file(dat_filename, tuples):
  ''' Write out the datapoints, sorted by the first tuple elt '''
  with open(dat_filename, "w") as dat:
    for tuple in tuples:
      stringified = map(lambda t: str(t), list(tuple))
      dat.write(" ".join(stringified) + "\n")

def write_template(gpi_filename, output_filename, name, dat_filename):
  with open(gpi_filename, "w") as gpi:
    gpi.write(template)
    gpi.write('''set output "%s"\n''' % output_filename)
    gpi.write('''set title "%s"\n''' %
              (name,))
    gpi.write('''plot "%s" using 1:2 title "High Income" w lp, ''' % (dat_filename,))
    gpi.write(''' "%s" using 1:3 title "Overall" w lp, ''' % (dat_filename,))
    gpi.write(''' "%s" using 1:4 title "Low & Middle Income" w lp\n''' % (dat_filename,))

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--sqlite-file',
                      default="../../data.sqlite", dest="db_file",
                      help='''sqlite grading database file''')
  args = parser.parse_args()

  db = None
  try:
    db = database.Database(args.db_file)
    cname2class = db.select_country_classifications()
    for hash, fetch_method in [(database.WTDNAME2CODE,db.select_wdi_classified_stats),
                               (database.WTINAME2COLUMN,db.select_wti_stats)]:
      for name, code in hash.iteritems():
        print "Examining %s %s" % (name, code,)
        tuples = fetch_method(code)
        year_classification2stats = assign_categories(tuples, cname2class)
        year_classification2stats = combine_categories(year_classification2stats)
        tuples = compute_averages(year_classification2stats)
        write_outputs(name, code, tuples)
  finally:
    if db:
      db.close()
