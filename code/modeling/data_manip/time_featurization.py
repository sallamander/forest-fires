from itertools import izip
from datetime import datetime

def add_date_column(df):
    '''
    Input: Pandas DataFrame
    Output Pandas DataFrame
    '''
        
    df['date_fire']=[datetime.strptime(date + "-" + str(gmt), "%Y-%m-%d-%H%M") for \
                    date, gmt in izip(df['date'].values, df['gmt'].values)]

    return df


