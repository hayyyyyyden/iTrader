import sys
sys.path.append("./")

import numpy as np
from datetime import datetime as dt
from datetime import datetime, timedelta

from core.strategy import Strategy
from core.event import SignalEvent
from core.backtest import Backtest
from core.data import HistoricCSVDataHandler
from core.execution import SimulatedExecutionHandler
from core.portfolio import NaivePortfolio

# Volatility Autocorrelation Strategy
class VolatilityAutocorrelationStrategy(Strategy):
    """
    Carries out a volatility autocorrelation strategy,
    R = volatility of past short window
    R2 = volatility of past long window
    K1: hyperparameter, 0.12 by default
    K2: hyperparameter, 0.32 by default
    Long limit at: open - R*k1
    Stoploss: 50 pip
    profit_target: R*k2
    Condition: c1 <= R2 < c2, 130 <= R2 < 190 by default
    """

    def __init__(self, bars, events, short_window=12, long_window=18,
                  sl = 50, k1=0.12, k2=0.32, c1=130, c2=190):
        """
        Initialises the Moving Average Cross Strategy.
        Parameters:
        bars - The DataHandler object that provides bar information
        events - The Event Queue object.
        short_window - 48 hours. if using 4H bar, then 12.
        long_window - 72 hours. if using 4H bar, then 18.
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.short_window = short_window
        self.long_window = long_window
        self.sl = sl
        self.k1 = k1
        self.k2 = k2
        self.c1 = c1
        self.c2 = c2
        # Set to True if a symbol is in the market
        self.bought = self._calculate_initial_bought()


    def _calculate_initial_bought(self):
        """
        Adds keys to the bought dictionary for all symbols
        and sets them to 'OUT'.
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = 'OUT'
        return bought

    def calculate_signals(self, event):
        """
        Generates a new set of signals based on the MAC
        SMA with the short window crossing the long window
        meaning a long entry and vice versa for a short entry.

        Parameters
        event - A MarketEvent object.
        """
        if event.type == 'MARKET':
            for s in self.symbol_list:
                highs = self.bars.get_latest_bars_values(
                    s, "high", N=self.long_window
                )
                lows = self.bars.get_latest_bars_values(
                    s, "low", N=self.long_window
                )
                close = self.bars.get_latest_bar_value(s, 'close')
                bar_date = self.bars.get_latest_bar_datetime(s)
                bar_date = datetime.strptime(bar_date[:-4], "%Y-%m-%dT%H:%M:%S.%f")
                if highs is not None and len(highs) == self.long_window and \
                   lows is not None and len(lows) == self.long_window:

                   R_max = np.max(highs[-self.short_window:])
                   R_min = np.min(lows[-self.short_window:])
                   R = (R_max - R_min) * 10000
                   R = round(R, 1)

                   R2_max = np.max(highs[-self.long_window:])
                   R2_min = np.min(lows[-self.long_window:])
                   R2 = (R2_max - R2_min) * 10000
                   R2 = round(R2, 1)

                   real_date = bar_date+timedelta(hours=4)
                   print('<----- K 线时间 {} -----> (当前实际时间是 {} 的第一秒)'.format(bar_date, real_date))
                   print('过去 {} 个小时, 最高价是 {}, 最低价是 {}. 波动值 R2 是 {} 个 Pips.'.format( 4*self.long_window, R2_max, R2_min, R2))
                   if R2 < self.c1 or R2 > self.c2:
                       print('当前 R2 波动值不满足限制条件: {} < R2 < {}'.format(self.c1, self.c2))
                       print('不交易，略过。\n\n')
                       return

                   print('当前 R2 波动值满足限制条件: {} < R2 < {} \n'.format(self.c1, self.c2))
                   print('过去 {} 个小时, 最高价是 {}, 最低价是 {}. 波动值 R 是 {} 个 Pips.'.format( 4*self.short_window, R_max, R_min, R))

                   buy_under = round(self.k1 * R, 1)
                   limit_price = round(close - buy_under/10000, 5)
                   print('当前价格是 {}. {} 倍的 R 是 {} 个 pips '.format(close,self.k1, buy_under))
                   print('开一个限价的买单 (Limit Buy Order) 在当前价格 {} 的 {} 个 pips 之下，即 {}.'.format(close, buy_under, limit_price))

                   profit_target = round(self.k2 * R, 1)
                   print('目标盈利 ( profit_target ) 是 {} 倍的 R，即 {} 个 pips.'.format(self.k2, profit_target))
                   profit_target = round(limit_price + profit_target / 10000, 5)
                   print('即, {}'.format(profit_target))
                   print('止损 (stop_loss) 为固定的 {} 个 pips.'.format(self.sl))
                   stop_loss = round(limit_price - self.sl / 10000, 5)
                   print('即, {}'.format(stop_loss))
                   signal_type = 'LONG'
                   signal = SignalEvent(s, real_date, signal_type, 'LMT',
                            limit_price, stop_loss, profit_target)
                   self.events.put(signal)


if __name__ == "__main__":
    csv_dir = './data/H4' # CHANGE THIS!
    symbol_list = ['AUD_USD_H4']
    initial_capital = 10000
    heartbeat = 0.0
    start_date = dt(2015, 1, 1, 0, 0, 0)
    backtest = Backtest(csv_dir, symbol_list, initial_capital,
                        heartbeat, start_date, HistoricCSVDataHandler,
                        SimulatedExecutionHandler, NaivePortfolio,
                        VolatilityAutocorrelationStrategy
    )
    backtest.simulate_trading()
