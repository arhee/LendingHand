"""feats.py

Functions to help create features

Author: Alex Rhee <alex.rhee@gmail.com>
"""

import pandas as pd
import numpy as np
import pickle
import pytz
import datetime

def create_credit_age(df):
    """
    Create the credit_age columns
    """
    now = pytz.utc.localize(datetime.datetime.now())
    p = now - df['earliest_cr_line']
    p = p.astype('timedelta64[D]')
    df['credit_age'] = p
    return df

def create_zeros(df):
    """
    Create the columns indicating if 0's up to that placeholder
    """ 
    #digits are zero
    for denom in [10, 100, 1000]:
        digits = df.loan_amnt/float(denom)
        digits -= digits.astype(int)
        digits = digits == 0
        digits = digits.astype(int)
        title = 'loan_' + str(denom) + 's'
        df[title] = digits
    return df

def get_time_units(df, cols):
    """ fragment the date columns given by col into component time units """
    for col in cols:
        name = col
        df['WeekDay_'+ name] = df[col].apply(lambda x: str(x.weekday()))
        df['Day_'+ name] = df[col].apply(lambda x: str(x.day))
        df['Month_'+ name] = df[col].apply(lambda x: str(x.month))
        df['Hour_'+ name] = df[col].apply(lambda x: str(x.hour))
    return df


def get_zip(s, num):
    if num > 2 or num < 1:
        raise Exception('Pick num = 1 or 2')
    return s[:num] + 'x'* (5-num)


def create_zip(df):
    df = df.rename(columns = {'zip_code':'3dig_zip_code'})
    df['2dig_zip_code'] = df['3dig_zip_code'].apply(lambda x: get_zip(x, 2))
    df['1dig_zip_code'] = df['3dig_zip_code'].apply(lambda x: get_zip(x, 1))
    return df


def encode_features(df, LE_fname):
    """
    Drops rows with features that are unfamiliar to the encoder
    Transforms remaining rows
    LE_dict - label encoder dict
    """
    
    LE_dict = pickle.load(open(LE_fname))
    LE_dict.pop("loan_status", None)
    LE_dict.pop("inc_categ", None)
    
    for col, le in LE_dict.iteritems():
        drop_these = ~df[col].isin(set(LE_dict[col].classes_))
        if drop_these.sum() > 0:
            df = df.drop(df[drop_these].index, axis=0)               
    for col, le in LE_dict.iteritems():
        df[col] = le.transform(df[col])
        
    return df