#!/Library/Frameworks/Python.framework/Versions/7.3/bin/python

# NumPy Correlation:
# numpy.corrcoef
# numpy.cov
# numpy.correlate
#
# Also: ANOVA

# TODO(cs): dunno what these are
# I think we might be trying to infer these!
(a_0, a_1, a_2, a_3, a_4, a_5, a_6) = (0,0,0,0,0,0,0)

# Level of real GDP per capita in 1980
# Code: NY.GDP.PCAP.PP.CD
GDP_80 = 0

# Average share of investment in GDP for 1980-2006
# Code: NE.GDI.TOTL.ZS
I_Y_8006 = 0

# Average telecommunications penetration per 100 people over 1980-2006
# Code; "Fixed broadband penetration"
TELEPEN_8006 = 0

# Primary school enrollment rate in 1980
# Code: SE.PRM.ENRR (gross, not net)
# Alternatively: secondary school: SE.SEC.NENR
# Tertiary school (university): SE.TER.ENRR
PRIM_80 = 0

# Dummy variable for countries in the Sub-Saharan Africa Region
# TODO(cs): why do we need these dummy variables?
SSA = 0

# Dummy variable for countries in the Latin America and Caribbean Region
LAC = 0

# TODO(cs): dunno what this is
mu = 0

def basic_regression():
  GDP_8006 = a_0 + a_1 * GDP_80 + a_2 * (I_Y_8006) + \
             a_3 * TELEPEN_8006 + a_4 * PRIM_80 + \
             a_5 * SSA + a_6 * LAC + mu

def differentiated_regresssion():
  # We also divided the sample into developed and develop-
  # ing economies (the latter including both middle-income and low-income
  # countries according to the World Bank country classifications),
  # created dummy variables, and generated the new variables TELEPENH and
  # TELEPENL (the product of the dummy variables and the telecommunications
  # penetration variables)
  pass

def tele_regression():
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
