"""NAR.py

Processing 

Interest calculating functions

Author: Alex Rhee <alex.rhee@gmail.com>
"""


def df2loans(df, zipcols, le_enc):
    """
    Turns the df into a list of loan dicts with attributes determined by zipcols
    """

    keepcols, newcolnames = zip(*zipcols)
    subdf = df[list(keepcols)]
    subdf = subdf.dropna()
    subdf.loc[:,'grade'] = le_enc['grade'].inverse_transform(subdf.grade)
    subdf.columns = newcolnames
    loans = subdf.to_dict('records')
    return loans
