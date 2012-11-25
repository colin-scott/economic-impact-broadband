#!/usr/bin/env python

# TODO(cs): dunno what these are
(a_0, a_1, a_2, a_3, a_4, a_5, a_6) = (0,0,0,0,0,0,0)

# Level of real GDP per capita in 1980
GDP_80 = 0

# Average share of investment in GDP for 1980–2006
I_Y_8006 = 0

# Average telecommunications penetration per 100 people over 1980–2006
TELEPEN_8006

# Primary school enrollment rate in 1980
PRIM_80 = 0

# Dummy variable for countries in the Sub-Saharan Africa Region
SSA = 0

# Dummy variable for countries in the Latin America and Caribbean Region
LAC = 0

# TODO(cs): dunno what this is
mu = 0

GDP_8006 = a_0 + a_1 * GDP_80 + a_2 * (I_Y_8006) + \
           a_3 * TELEPEN_8006 + a_4 * PRIM_80 + \
           a_5 * SSA + a_6 * LAC + mu
