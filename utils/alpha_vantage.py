from datetime import datetime as dt
import json

import pandas as pd
import requests

ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co'
ALPHA_VANTAGE_TIME_SERIES_CALL = 'query?function=TIME_SERIES_DAILY_ADJUSTED'
COLUMNS = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']

class AlphaVantage(object):
    """
    Encapsulates calls to the AlphaVantage API with a provided
    API key.
    """
    def __init__(self, api_key='YOUR_API_KEY_HERE'):
        """
        Initialise the AlphaVantage instance.
        Parameters
        ----------
        api_key : ‘str‘, optional
            The API key for the associated AlphaVantage account
        """
        self.api_key = api_key

    def _construct_alpha_vantage_symbol_call(self, ticker):
        """
        Construct the full API call to AlphaVantage based on the user
        provided API key and the desired ticker symbol.
        Parameters
        ----------
        ticker : 'str'
        The ticker symbol, e.g. 'AAPL'
        Returns
        -------
        'str'
            The full API call for a ticker time series
        """
        return "%s/%s&symbol=%s&outputsize=full&apikey=%s" % (
                ALPHA_VANTAGE_BASE_URL,
                ALPHA_VANTAGE_TIME_SERIES_CALL,
                ticker,
                self.api_key
                )

    def get_daily_historic_data(self, ticker, start_date, end_date):
        """
        Use the generated API call to query AlphaVantage with the
        appropriate API key and return a list of price tuples
        for a particular ticker.
        Parameters
        ----------
        ticker : ‘str‘
        The ticker symbol, e.g. 'AAPL'
        start_date : ‘datetime‘
        The starting date to obtain pricing for
        end_date : ‘datetime‘
            The ending date to obtain pricing for
        Returns
        -------
        ‘pd.DataFrame‘
        The frame of OHLCV prices and volumes
        """
        av_url = self._construct_alpha_vantage_symbol_call(ticker)
        try:
            av_data_js = requests.get(av_url)
            data = json.loads(av_data_js.text)['Time Series (Daily)']
        except Exception as e:
            print(
                "Could not download AlphaVantage data for %s ticker "
                "(%s)...stopping." % (ticker, e)
                )
            return pd.DataFrame(columns=COLUMNS).set_index('Date')
        else:
            prices = []
            for date_str in sorted(data.keys()):
                date = dt.strptime(date_str, '%Y-%m-%d')
                if date < start_date or date > end_date:
                    continue

                bar = data[date_str]
                prices.append(
                    (
                        date,
                        float(bar['1. open']),
                        float(bar['2. high']),
                        float(bar['3. low']),
                        float(bar['4. close']),
                        int(bar['6. volume']),
                        float(bar['5. adjusted close'])
                    )
                )
        return pd.DataFrame(prices, columns=COLUMNS).set_index('Date')


if __name__ == "__main__":
    # Create an AlphaVantage API instance
    av = AlphaVantage(api_key="Z5UZVXLKA7XOWF67")
    # Download the Apple Group OHLCV data from 1998-01-02 to 2008-12-31
    start_date = dt(1998, 1, 2)
    end_date = dt(2020, 4, 24)
    print("Obtaining Apple data from AlphaVantage and saving as CSV...")
    aapl = av.get_daily_historic_data('AAPL', start_date, end_date)
    aapl.to_csv("./data/xxx.csv", index=True)
