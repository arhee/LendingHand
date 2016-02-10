"""
The main engine of the app.  Takes in API data and processes it
"""

from LCfiles import NAR, cleanapi, feats, sparsify, proc2html
import pickle
import json


def run():
    # Variables

    URL = "https://api.lendingclub.com/api/investor/v1/loans/listing"
    KEY = "hdjiHts6C+hYUyMPyBQdzShmQSw="
    csv2api_fname = 'data/csv2api.json'
    emp_titles_fname = 'data/select_emp_titles.p'
    le_encoder_fname = 'data/le_encoder.p'
    sel_feats_fname = 'data/selected_feats2.json'
    col_order_fname = 'data/col_order.json'
    onehot_dict_fname = 'data/onehot_dict.p'

    #models

    default_model_fname = 'models/prob_def_model.p'
    pymnt_dur_model_fname = 'models/loan_dur_model.p'


    """
    Retrieve and Clean API data
    """

    df = cleanapi.ping_api(URL, KEY)
    df = cleanapi.rename_cols(df, csv2api_fname)

    # Processing Data
    df = cleanapi.proc_inc_verified(df)
    df = cleanapi.convert_date_cols(df)
    df = cleanapi.clean_txt_cols(df)
    df = cleanapi.drop_nullcols(df)
    df['initial_list_status'] = df.initial_list_status.apply(lambda x: x.lower())

    not_needed = ['member_id']
    df = df.drop(not_needed, axis=1)


    """
    Feature Engineering
    """

    select_emp_titles = pickle.load(open(emp_titles_fname))
    df = cleanapi.clean_emp_titles(df, select_emp_titles)
    df = feats.create_credit_age(df)
    df = feats.create_zeros(df)

    datecols = ['last_credit_pull_d', 'earliest_cr_line']
    feats.get_time_units(df, datecols)
    df = df.drop(datecols, axis=1)

    df['term'] = df.term.astype(str)
    df = feats.create_zip(df)


    """
    Feature Encoding
    """

    df = feats.encode_features(df, le_encoder_fname)
    sel_feats = json.load(open(sel_feats_fname))
    df = cleanapi.drop_any_null_rows(df[sel_feats['api'] + ['id']])


    """
    Sparsify the dataframe
    """

    col_order = json.load(open(col_order_fname))
    onehot_dict = pickle.load(open(onehot_dict_fname))

    cat_sparse_dict = sparsify.get_cat_sparse(df, onehot_dict)
    num_cols = list(set(sel_feats['api']) - set(cat_sparse_dict.keys()))
    num_sparse_dict = sparsify.get_sparse(df[num_cols])
    sparse_dict = sparsify.merge_two_dicts(cat_sparse_dict, num_sparse_dict)

    data = {'X':sparse_dict, 'order':col_order}
    X = sparsify.assemble_sparse(data)

    """
    Add NAR to the dataframe
    """
    default_model = pickle.load(open(default_model_fname))
    pymnt_dur_model = pickle.load(open(pymnt_dur_model_fname))


    def_preds = default_model.predict_proba(X)
    p_default, p_paid = zip(*def_preds)
    pred_term = pymnt_dur_model.predict(X)

    #place holder until linear model fixed

    df['pred_def_term'] = pred_term
    def_NAR = NAR.get_df_NAR(df, True)
    paid_NAR = NAR.get_df_NAR(df)
    pred_term = [20] * len(pred_term)

    expNAR, varNAR = NAR.get_meanvar_NAR(p_paid, paid_NAR, def_NAR)

    """
    Return NAR
    """

    default_model = pickle.load(open('models/prob_def_model.p'))
    pymnt_dur_model = pickle.load(open('models/loan_dur_model.p'))


    # Dummy to choose the default months 
    df = NAR.addNAR2df(default_model, pymnt_dur_model, df, X, 10)

    keepcols = ['loan_amnt', 'term', 'grade', 'expNAR', 'varNAR', 'id']
    newcolnames = ['loanAmount', 'term', 'grade', 'exp_int_rate', 'variance', 'id']

    zipcols = zip(keepcols, newcolnames)
    le_enc = pickle.load(open(le_encoder_fname))
    df['expNAR'] = df['expNAR'] * 100
    df['term'] = le_enc['term'].inverse_transform(df.term)
    loans = proc2html.df2loans(df, zipcols, le_enc)


    return loans