#!/Library/Frameworks/Python.framework/Versions/7.3/bin/python

import ols
import database
import sys
from scipy import stats
import scipy
from itertools import groupby

# NumPy Correlation:
#   numpy.corrcoef
#   numpy.cov
#   numpy.correlate
#
# Also: ANOVA
#   scipy.stats.stats.f_oneway
#   scipy.stats.stats.f_value

def select_classification(db, classification):
  class2cnames = db.select_class2cnames()
  ssa_countries = set(class2cnames[classification])
  countries_to_use = db.select_countries_to_use()
  dummy = []
  for country in countries_to_use:
    if country in ssa_countries:
      dummy.append(1)
    else:
      dummy.append(0)
  return dummy

def pad(tuples, start_year):
  # We assume that broadband penetration before first datapoint was zero
  new_groups = []
  for key, group in groupby(tuples, lambda t: t[1]):
    group = sorted(group, key=lambda t: t[0])
    minimum_year = group[0][0]
    index = 0
    for year in xrange(start_year, minimum_year):
      new_tuple = (year, key, 0)
      group.insert(index, new_tuple)
      index += 1
    new_groups += group
  return new_groups

def verify_country_order(tuples, db):
  # verify that we use all the same countries, in the same order
  countries_to_use = db.select_countries_to_use()
  for key, group in groupby(tuples, lambda t: t[1]):
    next = countries_to_use.pop(0)
    if key != next:
      raise ValueError("Country %s not expected %s" % (key,next,))

def average_datapoints(tuples):
  # Tuples are (year, country, value)
  #  - bucket by country
  #  - compute average per country
  #  - return list of averages
  new_averages = []
  for key, group in groupby(tuples, lambda t: t[1]):
    values = [ t[2] for t in group ]
    average = scipy.mean(values)
    new_averages.append(average)
  return new_averages

def get_basic_stats(db, tech_metric, pad_zeros=True, max_year=2012):
  initial_year = 1980
  db.populate_countries_to_use(tech_metric, max_year=max_year)

  # Average growth rate of real GDP per capita in US$ over 1980-2006
  GDP_8006 = [ tuple for tuple in
               db.select_wdi_stats("NY.GDP.MKTP.KD.ZG")
               if tuple[0] >= 1980 and tuple[0] <= max_year ]
  sys.stderr.write("Verifying GDP_8006\n")
  verify_country_order(GDP_8006, db)
  GDP_8006 = average_datapoints(GDP_8006)

  # Level of real GDP per capita in 1980
  GDP_80 = [ tuple for tuple in
             db.select_wdi_stats("NY.GDP.PCAP.KD")
             if tuple[0] == 1980 ]
  sys.stderr.write("Verifying GDP_80\n")
  verify_country_order(GDP_80, db)
  GDP_80 = [ tuple[2] for tuple in GDP_80 ]

  # Average share of investment in GDP for 1980-2006
  I_Y_8006 = [ tuple for tuple in
               db.select_wdi_stats("NE.GDI.TOTL.ZS")
               if tuple[0] >= 1980 and tuple[0] <= max_year ]
  sys.stderr.write("Verifying I_Y_8006\n")
  verify_country_order(I_Y_8006, db)
  I_Y_8006 = average_datapoints(I_Y_8006)

  # Average telecommunications penetration per 100 people over 1980-2006
  if tech_metric is not None:
    TELEPEN_8006 = [ tuple for tuple in
                     db.select_wti_stats(tech_metric)
                     if tuple[0] >= 1980 and tuple[0] <= max_year ]
    sys.stderr.write("Verifying TELEPEN_8006\n")
    # TODO(cs): fill in zeros for countries that are missing. Alternatively,
    # just list the # of countries used, as in Quiang's -1 table!
    verify_country_order(TELEPEN_8006, db)
    if pad_zeros:
      TELEPEN_8006 = pad(TELEPEN_8006, initial_year)
    TELEPEN_8006 = average_datapoints(TELEPEN_8006)

  # Primary school enrollment rate in 1980
  # Code: SE.PRM.ENRR (gross, not net)
  # Alternatively: secondary school: SE.SEC.NENR
  # Tertiary school (university): SE.TER.ENRR
  PRIM_80 = [ tuple for tuple in
              db.select_wdi_stats("SE.PRM.ENRR")
              if tuple[0] == 1980 ]
  sys.stderr.write("Verifying PRIM_80\n")
  verify_country_order(PRIM_80, db)
  PRIM_80 = [ tuple[2] for tuple in PRIM_80 ]

  # Dummy variable for countries in the Sub-Saharan Africa Region
  SSA = select_classification(db, "ssa")
  # Dummy variable for countries in the Latin America and Caribbean Region
  LAC = select_classification(db, "lac")
  return [GDP_8006, GDP_80, I_Y_8006, TELEPEN_8006, PRIM_80, SSA, LAC]

def regress_basic(db, tech_metric, pad_zeros=True, max_year=2012):
  datasets = get_basic_stats(db, tech_metric, pad_zeros=pad_zeros, max_year=max_year)
  GDP_8006 = scipy.array(datasets[0])
  independent_variables = scipy.array(datasets[1:])
  independent_variables = scipy.transpose(independent_variables)

  names = get_names(tech_metric)
  model = ols.ols(GDP_8006,independent_variables,
                  'GDP_8006',names)
  print "# Countries: %d" % len(db.select_countries_to_use())
  model.summary()

  # ANOVA:
  #f_val, p_val = stats.f_oneway(GDP_8006, GDP_80, I_Y_8006,
  #                              TELEPEN_8006, PRIM_80, SSA, LAC)
  #print f_val
  #print p_val

def differentiated_regression(db, tech_metric, pad_zeros=True, max_year=2012):
  # We also divided the sample into developed and develop-
  # ing economies (the latter including both middle-income and low-income
  # countries according to the World Bank country classifications),
  # created dummy variables, and generated the new variables TELEPENH and
  # TELEPENL (the product of the dummy variables and the telecommunications
  # penetration variables)
  datasets = get_basic_stats(db, tech_metric, pad_zeros=pad_zeros, max_year=max_year)
  high_income = select_classification(db, "high")
  datasets.append(high_income)
  # TODO(cs): tried adding in low income too, but that totally throws off the
  #           results
  GDP_8006 = scipy.array(datasets[0])
  independent_variables = scipy.array(datasets[1:])
  independent_variables = scipy.transpose(independent_variables)

  names = get_names(tech_metric)
  model = ols.ols(GDP_8006,independent_variables,
                  'GDP_8006',names)
  print "# Countries: %d" % len(db.select_countries_to_use())
  model.summary()

def get_names(tech_metric):
  if tech_metric is not None:
    names = ['GDP_80','I_Y',tech_metric,'PRIM','SSA','LAC']
  else:
    names = ['GDP_80','I_Y','PRIM','SSA','LAC']
  return names

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
    for max_year in [2006, 2011]:
      # FIXED - Number of main lines - "inet_per_100"
      # MOBILE - Number of mobile suscribers - "mobile_per_100"
      # INTERNET - Number of Internet users - "inter_percent"
      # BBND - Number of Broadband susccribers - "broadband_per_100"
      for tech_metric in ["inet_per_100", "broadband_per_100",
                          "mobile_per_100"]:
        for pad_zeros in [True, False]:
          print "Max year: ", max_year
          print "Pad zeros: ", pad_zeros
          print "Tech metric: ", tech_metric
          regress_basic(db, tech_metric, pad_zeros=pad_zeros, max_year=max_year)
          differentiated_regression(db, tech_metric, pad_zeros=pad_zeros, max_year=max_year)
  finally:
    if db:
      db.close()

