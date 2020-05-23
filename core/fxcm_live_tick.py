from .data import DataHandler
from fxcmpy import fxcmpy


def _fxcm_symbol_from(symbol):
    if symbol == 'AUD_USD':
        return 'AUD/USD'


class FXCMLiveTickDataHandler:

    def __init__(self, events, csv_dir, symbol_list, start_date):
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list

        self.fxcm_api_wrapper = fxcmpy(config_file='fxcm.cfg', server='demo')
        for symbol in symbol_list:
            fxcm_symbol = _fxcm_symbol_from(symbol)
            self.fxcm_api_wrapper.subscribe_market_data(fxcm_symbol, self.on_prices_update)
        self.tick_data = {}
        self.bar_data = _prepare_bar_data(symbol_list)
        self.lastest_tick_event = None
        self.continue_backtest = True

    def _prepare_bar_data(self):
        # 1. 先检查现有的本地数据的最新一条数据的时间
        # 2. 然后调API来更新最后一条数据到当前时间的历史数据，并存储到本地（这个应该每天定期做？
        # 3. 然后再把数据读取到内存里
        pass

    # 1 | EUR/USD | 2018-06-06 10:06:29.800000, 1.17725, 1.17749, 1.17756, 1.17095
    # 2 | EUR/USD | 2018-06-06 10:06:34.421000, 1.17725, 1.17748, 1.17756, 1.17095
    # 为什么不能在这里把 Tick Event 放到 Event Queue 里，而一定要在 Backtest 里主动调取？我试试有什么区别
    def on_prices_update(self, data, dataframe):
        # 1. 把最新的 dataframe 的数据存储到
        self.tick_data[data.symbol] = dataframe
        # 2. 更新最新的 tick event
        tick_event = self._create_event(data)
        if self.price_event is not None:
            # 难道原因是这个速度太快？
            print("losing %s" % self.price_event)
        self.tick_event = tick_event
        # 3. 更新 bar data，如果有更新，新建一个bardata的事件
        # 想一下，更新 bar 的逻辑，是按照当前系统的时间，还是收到的tick的时间
        if self._update_bar_data(dataframe):
            self.events.put(MarketEvent())

    def _update_bar_data(self, symbol):
        # self.tickers[symbol].lastest
        # 1. 检查当前的bar data 是不是缺少最近一分钟的数据
        # 2. 从当前的临时 tick 数据中合成最近一分钟的 OHLC 的 ask 和 bid 数据
        # 3. 添加到当前的 bar data 中的最后一条
        # 4. 如果有更新，返回true，没有返回false，让外部继续下一步
        return True

    def _create_event(self, data):
        ticker = data["Symbol"]
        index = pd.to_datetime(datetime.datetime.fromtimestamp(float(data["Updated"])/1000))
        bid = PriceParser.parse(data["Rates"][0])
        ask = PriceParser.parse(data["Rates"][1])
        return TickEvent(ticker, index, bid, ask)

    def _store_event(self, event):
        """
        Store price event for bid/ask
        """
        ticker = event.ticker
        self.tickers[ticker]["bid"] = event.bid
        self.tickers[ticker]["ask"] = event.ask
        self.tickers[ticker]["timestamp"] = event.time

    def stream_next(self):
        """
        Place the next PriceEvent (BarEvent or TickEvent) onto the event queue.
        """
        if self.price_event is not None:
            self.events_queue.put(self.tick_event)
            self.tick_event = None