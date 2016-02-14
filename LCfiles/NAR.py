"""NAR.py

Net Annualized Return 
https://www.lendingclub.com/public/lendersPerformanceHelpPop.action

Interest calculating functions

Author: Alex Rhee <alex.rhee@gmail.com>
"""

import pandas as pd

def get_df_NAR(df, default=False):
    """
    Retrieves NAR for a dataframe
    Assumes
    .loan_amnt
    .installment
    .pred_def_term
    .term
    """
    narlist = []
    if default:
        for ix, row in df.iterrows():
            narlist.append(get_NAR(row.int_rate/1200, row.loan_amnt, row.installment, row.pred_def_term, default))            
    else:
        for ix, row in df.iterrows():
            if row.term == 1:
                term = 36
            else:
                term = 60
            narlist.append(get_NAR(row.int_rate/1200, row.loan_amnt, row.installment, term, default))
    return pd.Series(narlist)

def get_NAR(rate, prncp, installment, periods, default):
    """
        Calculates the net annualized return for a loan inclusive of fees
        rate is monthly rate = annual rate / 12
        n = # of periods
    """
    tot_int = 0.
    tot_prncp = 0.
    fee = 0.01*installment

    for _ in range(int(periods)):
        tot_int += rate * prncp - fee
        tot_prncp += prncp
        prncp -= installment - rate * prncp

    tot_int -= default * prncp
    return (1+tot_int/tot_prncp)**12 -1

def get_meanvar_NAR(p_paid, NAR, def_NAR):
    """
    Retrieves the expected NAR value and the variance

    NAR and def_NAR are the NAR for paid and default in pd.Series format
    """

    p_def = [1-x for x in p_paid]
    expNAR = p_paid * NAR + p_def * def_NAR
    meanNAR = (NAR + def_NAR)/2
    varNAR = p_paid * (NAR - meanNAR)**2 + p_def * (def_NAR - meanNAR)**2
    varNAR = varNAR /2
    return expNAR, varNAR

def addNAR2df(default_model, dur_model, df, X, dummy=None):
    def_preds = default_model.predict_proba(X)
    p_default, p_paid = zip(*def_preds)
    pred_term = dur_model.predict(X)
    
    if dummy:
        pred_term = [dummy] * len(pred_term)
    
    df['pred_def_term'] = pred_term
    def_NAR = get_df_NAR(df, True)
    paid_NAR = get_df_NAR(df)
    expNAR, varNAR = get_meanvar_NAR(p_paid, paid_NAR, def_NAR)
    df['expNAR'] = expNAR.values
    df['varNAR'] = varNAR.values
    return df
    