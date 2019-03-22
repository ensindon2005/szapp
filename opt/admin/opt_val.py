# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 10:58:20 2018

@author: sz08641
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy import stats
import datetime as dt
import matplotlib as mpl
mpl.rcParams['font.family'] = 'serif'






def dN(x):
    ''' Probability density function of standard normal random variable x. '''
    return math.exp(-0.5 * x ** 2) / math.sqrt(2 * math.pi)


def N(d):
    ''' Cumulative density function of standard normal random variable x. '''
    return quad(lambda x: dN(x), -20, d, limit=50)[0]


def d1f(S0, K, T, r, sigma):
    ''' Black-Scholes-Merton d1 function.
        Parameters see e.g. BSM_call_value function. '''
    d1 = (math.log(S0 / K) + (r + 0.5 * sigma ** 2)
          * (T)) / (sigma * math.sqrt(T))
    return d1


def BSM_call_value(S0, K, T, r, sigma):
#""" 
#Valuation of European call option in BSM model.
#    Analytical formula.
#    
#    Parameters
#    ==========
#    S0 : float
#        initial stock/index level
#    K : float
#        strike price
#    T : float
#        maturity date (in year fractions)
#    r : float
#        constant risk-free short rate
#    sigma : float
#        volatility factor in diffusion term
#    
#    Returns
#    =======
#    value : float
#        present value of the European call option """

    
    
    S0 = float(S0)
    d1 = (math.log(S0 / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = (math.log(S0 / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    value = round((S0 * stats.norm.cdf(d1, 0.0, 1.0)
            - K * math.exp(-r * T) * stats.norm.cdf(d2, 0.0, 1.0)),3)
      # stats.norm.cdf --> cumulative distribution function
      #                    for normal distribution
    return value






def BSM_put_value(S0, K, T, r, sigma):
    ''' Calculates Black-Scholes-Merton European put option value.

    Parameters
    ==========
    S0 : float
        stock/index level at time t
    K : float
        strike price
    
    T : float
        maturity date (in year fractions)
    r : float
        constant, risk-less short rate
    sigma : float
        volatility

    Returns
    =======
    put_value : float
        European put present value at t
    '''
    
    #put=round( K*-S0*stats.norm.cdf(d1, 0.0, 1.0))
    put_value = BSM_call_value(S0, K, T, r, sigma) \
        - S0 + math.exp(-r * (T)) * K
    return put_value

    

