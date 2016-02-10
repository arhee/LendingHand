"""sparsify.py

Functions to help create features

Author: Alex Rhee <alex.rhee@gmail.com>
"""

import pandas as pd
import numpy as np
import pickle
import pytz
from scipy import sparse

def get_sparse(df):
    """
    Takes in dataframe
    Returns dict of sparse matrices
    """
    sparse_dict = {}
    for col in df.columns:
        sparse_dict[col] = sparse.csr_matrix(pd.DataFrame(df[col]))
    return sparse_dict

def assemble_sparse(data):
    """
    Given the a dict with properties 'X', 'order',
    return a sparse matrix
    """
    sparse_dict = data['X']
    sparse_list = []
    for col in data['order']:
        sparse_list.append(sparse_dict[col])
    X = sparse.hstack(sparse_list)
    return X

def get_onehot_dict(df, onehot_dict):
    """
    Given a dataframe, and a dictionary of onehot encoders,
    return a dictionary of sparse matrices
    """
    sparse_dict = {}
    for col, ohc in onehot_dict.iteritems():
        onehotcol = ohc.transform(pd.DataFrame(df[col]))
        sparse_dict[col] = onehotcol
    return sparse_dict

def merge_two_dicts(x, y):
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    z = x.copy()
    z.update(y)
    return z

def get_cat_sparse(df, onehot_dict):
    """
    Retrieves the sparsified dict of categories given by the onehot dict
    """
    cat_sparse_dict = {}
    for col, ohc in onehot_dict.iteritems():
        cat_sparse_dict[col] = ohc.transform(pd.DataFrame(df[col]))
    return cat_sparse_dict