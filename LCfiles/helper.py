"""helper.py

Net Annualized Return 
https://www.lendingclub.com/public/lendersPerformanceHelpPop.action

Interest calculating functions

Author: Alex Rhee <alex.rhee@gmail.com>
"""

def ping_api():
    """Pings the lendingclub API for the most recent data"""

    url = "https://api.lendingclub.com/api/investor/v1/loans/listing"
    key = "hdjiHts6C+hYUyMPyBQdzShmQSw="
    req = requests.get(url, headers={'Authorization': key})
    json_data = req.json()
    return pd.DataFrame(json_data['loans'])

def rename_cols(df,fname):
    """
    Renames the API df columns to LC CSV format.
    fname is the dictionary that translates API to CSV cols
    """
    fullcols = json.load(open(fname))
    final_cols = fullcols.values()
    newcols = [fullcols[x] if fullcols.get(x, None) else x for x in df.columns]
    df.columns = newcols
    df = df[final_cols]
    return df

def proc_inc_verified(df):
    """
    Processes income verification
    """
    df['verification_status'] = df.verification_status.apply(lambda x: x.replace("_"," "))
    return df
    

def str2date(x):
    """
    String to datetime format
    """
    if type(x) in (str, unicode):
        return parser.parse(x)
    else:
        return None

def convert_date_cols(df):
    """
    Convert all the datetime columns
    """
    datecols = ['earliest_cr_line','last_credit_pull_d']
    for col in datecols:
        df[col] = df[col].apply(lambda x: str2date(x))
    return df

def clean_txt(txt):
    """
    transform a text string to lower case and only alphanumeric
    """
    if type(txt) not in (str, unicode):
        return None
    lowerdigitsspace = set(string.lowercase + string.digits + ' ')
    letters = [x for x in txt.lower() if x in lowerdigitsspace]
    splited = "".join(letters).split()
    return " ".join(splited)

def clean_txt_cols(df):
    """
    Hard coded - clean the text columns
    """
    df['emp_title'] = df.emp_title.apply(lambda x: clean_txt(x))
    df['verification_status'] = df.verification_status.apply(lambda x: x.lower())
    return df

def drop_nullcols(df):
    """
    Drop the null columns
    """
    nullcounts = df.isnull().sum()
    nullcols = nullcounts[nullcounts == df.shape[0]].index
    df = df.drop(nullcols, axis=1)
    return df

def clean_emp_titles(df, select_emp_titles):
    """
    Fill the NaN values with unknown
    Change any titles not included in the model to unknown
    """
    # if columns is NaN change to unknown
    ix = df[df.emp_title.isnull()].index
    df.loc[ix, 'emp_title'] = "unknown"
    
    # if employee titles are not included in model change to unknown
    sel = ~df.emp_title.isin(select_emp_titles)
    ix = sel[sel==True].index

    #replace those nonrecognized titles with unknown
    df.loc[ix, 'emp_title'] = 'unknown'
    
    return df

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

def get_zip(s, num):
    if num > 2 or num < 1:
        raise Exception('Pick num = 1 or 2')
    return s[:num] + 'x'* (5-num)


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

def drop_any_null_rows(df):
    """
    Drop rows with any NaN values
    """
    nullrows = df.isnull().any(axis=1)
    nullidx = nullrows[nullrows].index
    df = df.drop(nullidx, axis=0)   
    return df