#!/Library/Frameworks/Python.framework/Versions/7.3/bin/python

import ols
import database
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

def get_basic_stats(db, pad_zeros=True, max_year=2012):
  initial_year = 1980

  # Average growth rate of real GDP per capita in US$ over 1980-2006
  GDP_8006 = [ tuple for tuple in
               db.select_wdi_stats("NY.GDP.MKTP.KD.ZG")
               if tuple[0] >= 1980 and tuple[0] <= max_year ]
  print "Verifying GDP_8006"
  verify_country_order(GDP_8006, db)
  GDP_8006 = average_datapoints(GDP_8006)

  # Level of real GDP per capita in 1980
  GDP_80 = [ tuple for tuple in
             db.select_wdi_stats("NY.GDP.PCAP.KD")
             if tuple[0] == 1980 ]
  print "Verifying GDP_80"
  verify_country_order(GDP_80, db)
  GDP_80 = [ tuple[2] for tuple in GDP_80 ]

  # Average share of investment in GDP for 1980-2006
  I_Y_8006 = [ tuple for tuple in
               db.select_wdi_stats("NE.GDI.TOTL.ZS")
               if tuple[0] >= 1980 and tuple[0] <= max_year ]
  print "Verifying I_Y_8006"
  verify_country_order(I_Y_8006, db)
  I_Y_8006 = average_datapoints(I_Y_8006)

  # Average telecommunications penetration per 100 people over 1980-2006
  TELEPEN_8006 = [ tuple for tuple in
                   db.select_wti_stats("broadband_per_100")
                   if tuple[0] >= 1980 and tuple[0] <= max_year ]
  print "Verifying TELEPEN_8006"
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
  print "Verifying PRIM_80"
  verify_country_order(PRIM_80, db)
  PRIM_80 = [ tuple[2] for tuple in PRIM_80 ]

  # Dummy variable for countries in the Sub-Saharan Africa Region
  SSA = select_classification(db, "ssa")
  # Dummy variable for countries in the Latin America and Caribbean Region
  LAC = select_classification(db, "lac")
  return [GDP_8006, GDP_80, I_Y_8006, TELEPEN_8006, PRIM_80, SSA, LAC]

def regress_basic(db, pad_zeros=True, max_year=2012):
  datasets = get_basic_stats(db, pad_zeros=pad_zeros, max_year=max_year)
  GDP_8006 = scipy.array(datasets[0])
  independent_variables = scipy.array(datasets[1:])
  independent_variables = scipy.transpose(independent_variables)

  model = ols.ols(GDP_8006,independent_variables,
                  'GDP_8006',['GDP_80', 'I_Y','TELEPEN','PRIM','SSA','LAC'])
  model.summary()

  # ANOVA:
  #f_val, p_val = stats.f_oneway(GDP_8006, GDP_80, I_Y_8006,
  #                              TELEPEN_8006, PRIM_80, SSA, LAC)
  #print f_val
  #print p_val

def differentiated_regression(db, pad_zeros=True, max_year=2012):
  # We also divided the sample into developed and develop-
  # ing economies (the latter including both middle-income and low-income
  # countries according to the World Bank country classifications),
  # created dummy variables, and generated the new variables TELEPENH and
  # TELEPENL (the product of the dummy variables and the telecommunications
  # penetration variables)
  datasets = get_basic_stats(db, pad_zeros=pad_zeros, max_year=max_year)
  high_income = select_classification(db, "high")
  datasets.append(high_income)
  # TODO(cs): tried adding in low income too, but that totally throws off the
  # results
  GDP_8006 = scipy.array(datasets[0])
  independent_variables = scipy.array(datasets[1:])
  independent_variables = scipy.transpose(independent_variables)

  model = ols.ols(GDP_8006,independent_variables,
                  'GDP_8006',['GDP_80', 'I_Y','TELEPEN','PRIM','SSA','LAC',
                              'H'])
  model.summary()

def tele_regression(db):
  # Number of main lines
  FIXED = 0
  # Number of mobile suscribers
  MOBILE = 0
  # Number of Internet users
  INTERNET = 0
  # Number of Broadband susccribers
  BBND = 0
  # High-income countries
  H = 0
  # Low and middle income countries
  L = 0

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
    for pad_zeros in [True, False]:
      print "Pad zeros: ", pad_zeros
      regress_basic(db, pad_zeros=pad_zeros, max_year=2006)
      differentiated_regression(db, pad_zeros=pad_zeros, max_year=2006)
  finally:
    if db:
      db.close()

