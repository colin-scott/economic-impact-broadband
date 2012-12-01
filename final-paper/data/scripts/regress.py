#!/Library/Frameworks/Python.framework/Versions/7.3/bin/python

import ols
import database
import random
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

def pad_zeros(tuples, start_year):
  # We assume that broadband penetration before first datapoint was zero
  new_groups = []
  for key, group in groupby(tuples, lambda t: t[1]):
    group = sorted(group, key=lambda t: t[0])
    minimum_year = group[0][0]
    for year in xrange(start_year, minimum_year):
      new_tuple = (year, key, 0)
      group.insert(0, new_tuple)
    new_groups.append(group)
  return new_groups

def average_datapoints(tuples):
  # Tuples are (year, country, value)
  #  - bucket by country
  #  - compute average per country
  #  - return list of averages
  # TODO(cs): verify that this keeps the same order of countries
  new_averages = []
  import pdb; pdb.set_trace()
  for key, group in groupby(tuples, lambda t: t[1]):
    values = [ t[2] for t in group ]
    average = scipy.mean(values)
    new_averages.append(average)
  return new_averages

def normalize_sample_sizes(datasets):
  new_datasets = []
  min_length = min([len(a) for a in datasets])
  for dataset in datasets:
    subset = random.sample(dataset, min_length)
    new_datasets.append(subset)
  return new_datasets

def get_basic_stats(db):
  # TODO(cs): remove sanity check Quiang's result: filter after 2006
  initial_year = 1980

  # Average growth rate of real GDP per capita in US$ over 1980-2006
  GDP_8006 = [ tuple for tuple in
               db.select_wdi_stats("NY.GDP.MKTP.KD.ZG")
               if tuple[0] >= 1980 and tuple[0] <= 2006 ]
  GDP_8006 = average_datapoints(GDP_8006)

  # Level of real GDP per capita in 1980
  GDP_80 = [ tuple[2] for tuple in
             db.select_wdi_stats("NY.GDP.PCAP.KD")
             if tuple[0] == 1980 ]

  # Average share of investment in GDP for 1980-2006
  I_Y_8006 = [ tuple for tuple in
               db.select_wdi_stats("NE.GDI.TOTL.ZS")
               if tuple[0] >= 1980 and tuple[0] <= 2006]
  I_Y_8006 = average_datapoints(I_Y_8006)

  # Average telecommunications penetration per 100 people over 1980-2006
  # TODO(cs): need to ensure that countries are lined up
  TELEPEN_8006 = [ tuple for tuple in
                   db.select_wti_stats("broadband_per_100")
                   if tuple[0] >= 1980 and tuple[0] <= 2006]
  TELEPEN_8006 = pad_zeros(TELEPEN_8006, initial_year)
  TELEPEN_8006 = average_datapoints(TELEPEN_8006)

  # Primary school enrollment rate in 1980
  # Code: SE.PRM.ENRR (gross, not net)
  # Alternatively: secondary school: SE.SEC.NENR
  # Tertiary school (university): SE.TER.ENRR
  PRIM_80 = [ tuple[2] for tuple in
              db.select_wdi_stats("SE.PRM.ENRR")
              if tuple[0] == 1980 ]

  min_length = min([len(a) for a in
                    [GDP_8006, GDP_80, I_Y_8006, TELEPEN_8006, PRIM_80]])

  # Dummy variable for countries in the Sub-Saharan Africa Region
  # TODO(cs): I believe these are 1 if the country is in the region, 0
  # otherwise. This implies that there are exactly 120 data points! (she
  # collapsed the years into averages)
  #SSA = [1] * min_length

  ## Dummy variable for countries in the Latin America and Caribbean Region
  #LAC = [1] * min_length
  return [GDP_8006, GDP_80, I_Y_8006, TELEPEN_8006, PRIM_80] #, SSA, LAC]

def regress_basic(db):
  datasets = get_basic_stats(db)

  datasets = normalize_sample_sizes(datasets)
  GDP_8006 = scipy.array(datasets[0])
  independent_variables = scipy.array(datasets[1:])
  independent_variables = scipy.transpose(independent_variables)

  model = ols.ols(GDP_8006,independent_variables,
                  'GDP_8006',['GDP_80', 'I_Y','TELEPEN','PRIM'])#,'SSA','LAC'])
  model.summary()

  # ANOVA:
  #f_val, p_val = stats.f_oneway(GDP_8006, GDP_80, I_Y_8006,
  #                              TELEPEN_8006, PRIM_80, SSA, LAC)
  #print f_val
  #print p_val

def differentiated_regresssion(db):
  # We also divided the sample into developed and develop-
  # ing economies (the latter including both middle-income and low-income
  # countries according to the World Bank country classifications),
  # created dummy variables, and generated the new variables TELEPENH and
  # TELEPENL (the product of the dummy variables and the telecommunications
  # penetration variables)
  pass

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
    regress_basic(db)
  finally:
    if db:
      db.close()

