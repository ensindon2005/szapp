from opt import db
from opt.models import *



def get_instruments():      
    instruments=Instrument.query
    return instruments

def get_futures():
    futures=Futures.query
    return futures

def get_months():
    month=MonthC.query
    return month

def get_futc():
    futctr=FutContract.query
    return futctr