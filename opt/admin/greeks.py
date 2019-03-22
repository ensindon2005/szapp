# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 11:26:34 2018

@author: sz08641
"""

#
# Black-Scholes-Merton (1973) European Call Option Greeks
# 05_com/BSM_call_greeks.py
#
# (c) Dr. Yves J. Hilpisch
# Derivatives Analytics with Python
#
import math
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
from opt.admin.opt_val import d1f, N, dN
mpl.rcParams['font.family'] = 'serif'

#
# Functions for Greeks
#

def BSM_delta(S0, K, T, r, sigma):
    ''' Black-Scholes-Merton DELTA of European call option.

    Parameters
    ==========
    S0 : float
        stock/index level at time t
    K : float
        strike price
    T : time in year proportion
    r : float
        constant, risk-less short rate
    sigma : float
        volatility

    Returns
    =======
    delta : float
        European call option DELTA
    '''
    d1 = d1f(S0, K, T, r, sigma)
    delta = N(d1)
    return delta


def BSM_gamma(S0, K, T, r, sigma):
    ''' Black-Scholes-Merton GAMMA of European call option.

    Parameters
    ==========
    S0 : float
        stock/index level at time t
    K : float
        strike price
    T : time in year proportion
    r : float
        constant, risk-less short rate
    sigma : float
        volatility


    Returns
    =======
    gamma : float
        European call option GAMM and PUT GAMMA
    '''
    d1 = d1f(S0, K, T, r, sigma)
    gamma = dN(d1) / (S0 * sigma * math.sqrt(T))
    return gamma


def BSM_theta(S0, K, T, r, sigma):
    ''' Black-Scholes-Merton THETA of European call option.

    Parameters
    ==========
     S0 : float
        stock/index level at time t
    K : float
        strike price
    T : time in year proportion
    r : float
        constant, risk-less short rate
    sigma : float
        volatility

    Returns
    =======
    theta : float
        European call option THETA
    '''
    d1 = d1f(S0, K, T, r, sigma)
    d2 = d1 - sigma * math.sqrt(T)
    theta_year= -(S0 * dN(d1) * sigma / (2 * math.sqrt(T)) +
              r * K * math.exp(-r * (T)) * N(d2))
    theta = theta_year/365
    return theta


def BSM_rho(S0, K, T, r, sigma):
    ''' Black-Scholes-Merton RHO of European call option.

#    Parameters
#    ==========
#    S0 : float
#        stock/index level at time t
#    K : float
#        strike price
#    T : time in year proportion
#    r : float
#        constant, risk-less short rate
#    sigma : float
#        volatility
#
#    Returns
#    =======
#    rho : float
#        European call option RHO
#    '''
    d1 = d1f(S0, K, T, r, sigma)
    d2 = d1 - sigma * math.sqrt(T)
    rho = (K * (T) * math.exp(-r * (T)) * N(d2))/100
    return rho


def BSM_vega(S0, K, T, r, sigma):
    ''' Black-Scholes-Merton VEGA of European call option.

    Parameters
    ==========
     S0 : float
        stock/index level at time t
    K : float
        strike price
    T : time in year proportion
    r : float
        constant, risk-less short rate
    sigma : float
        volatility


    Returns
    =======
    vega : float
        European call option VEGA
    '''
    d1 = d1f(S0, K, T, r, sigma)
    vega_full = S0 * dN(d1) * math.sqrt(T)
    vega = vega_full/100
    return vega


"""FROM here start the GREEKS FOR PUTS -->GAMMA and VEGA are the same for call and puts"""

def BSM_delta_put(S0, K, T, r, sigma):
    ''' Black-Scholes-Merton DELTA of European call option.

    Parameters
    ==========
    S0 : float
        stock/index level at time t
    K : float
        strike price
    T : time in year proportion
    r : float
        constant, risk-less short rate
    sigma : float
        volatility

    Returns
    =======
    delta : float
        European call option DELTA
    '''
    d1 = d1f(S0, K, T, r, sigma)
    delta = N(d1)-1
    return delta


def BSM_theta_put(S0, K, T, r, sigma):
    ''' Black-Scholes-Merton THETA of European call option.

    Parameters
    ==========
     S0 : float
        stock/index level at time t
    K : float
        strike price
    T : time in year proportion
    r : float
        constant, risk-less short rate
    sigma : float
        volatility

    Returns
    =======
    theta : float
        European call option THETA
    '''
    d1 = d1f(S0, K, T, r, sigma)
    d2 = d1 - sigma * math.sqrt(T)
    theta_year= -(S0 * dN(d1) * sigma / (2 * math.sqrt(T)) +
              r * K * math.exp(-r * (T)) * N(d2))
    theta = theta_year/365
    return theta


def BSM_rho_put(S0, K, T, r, sigma):
    ''' Black-Scholes-Merton RHO of European call option.

#    Parameters
#    ==========
#    S0 : float
#        stock/index level at time t
#    K : float
#        strike price
#    T : time in year proportion
#    r : float
#        constant, risk-less short rate
#    sigma : float
#        volatility
#
#    Returns
#    =======
#    rho : float
#        European call option RHO
#    '''
    d1 = d1f(S0, K, T, r, sigma)
    d2 = d1 - sigma * math.sqrt(T)
    rho = (K * (-T) * math.exp(-r * (T)) * N(-d2))/100
    return rho

