from datetime import datetime as dt, timedelta as td
import os
import sys
sys.path.append(os.path.join('..', 'data'))
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import (
    LinearDiscriminantAnalysis as LDA,
    QuadraticDiscriminantAnalysis as QDA
)
from sklearn.metrics import confusion_matrix
from sklearn.svm import LinearSVC, SVC
from alpha_vantage import AlphaVantage

def create_lagged_series(symbol, start_date, end_date, lags=5):
    """
    This creates a Pandas DataFrame that stores the
    percentage returns of the adjusted closing value of
    a stock obtained from AlphaVantage, along with a
    number of lagged returns from the prior trading days
    (lags defaults to 5 days). Trading volume, as well as
    the Direction from the previous day, are also included.
    Parameters
    ----------
    av : ‘AlphaVantage‘
        The AlphaVantage API instance used to obtain pricing
    symbol : ‘str‘
    The ticker symbol to obtain from AlphaVantage
    start_date : ‘datetime‘
    The starting date of the series to obtain
    end_date : ‘datetime‘
        The ending date of the the series to obtain
    lags : ‘int‘, optional
        The number of days to 'lag' the series by
    Returns
    -------
    'pd.DataFrame'
    Contains the Adjusted Closing Price returns and lags
    """
    # Obtain stock pricing from AlphaVantage
    adj_start_date = start_date - td(days=365)
    ts = av.get_daily_historic_data(symbol, adj_start_date, end_date)
    # Create the new lagged DataFrame
    tslag = pd.DataFrame(index=ts.index)
    tslag['Today'] = ts['Adj Close']
    tslag['Volume'] = ts['Volume']

    # Create the shifted lag series of prior trading period close values
    for i in range(0, lags):
        tslag['Lag%s' % str(i+1)] = ts['Adj Close'].shift(i+1)

    # Create the returns DataFrame
    tsret = pd.DataFrame(index=tslag.index)
    tsret['Volume'] = tslag['Volume']
    tsret['Today'] = tslag['Today'].pct_change() * 100.0

    # If any of the values of percentage returns equal zero, set them to
    # a small number (stops issues with QDA model in scikit-learn)
    tsret.loc[tsret['Today'].abs() < 0.0001, ['Today']] = 0.0001

    # Create the lagged percentage returns columns
    for i in range(0, lags):
        tsret['Lag%s' % str(i+1)] = \
            tslag['Lag%s' % str(i+1)].pct_change() * 100.0
    # Create the "Direction" column (+1 or -1) indicating an up/down day
    tsret['Direction'] = np.sign(tsret['Today'])
    tsret = tsret[tsret.index >= start_date]

    return tsret
