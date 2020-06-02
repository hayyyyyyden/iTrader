import os
from datetime import datetime, timedelta

import pandas as pd
from fxcmpy import fxcmpy

from core.event import TickEvent, MarketEvent, OrderEvent, SignalEvent
from core.fxcm_execution import FXCMExecutionHandler

fxcm_symbol_from = {
    'AUD_USD': 'AUD/USD',
    'EUR_USD': 'EUR/USD'
}


def _continue_loop_condition(dh):
    if datetime.now() > dh.end_datetime:
        print("时间到")
        dh.disconnect()
        return False
    else:
        return True


class FXCMLiveTickDataHandler:

    def __init__(self, events_queue, csv_dir, symbol_list, end_datetime):
        self.events_queue = events_queue
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.fxcm_conn = self.create_fxcm_connection()
        self.end_datetime = end_datetime
        print("结束时间", self.end_datetime)
        self.tick_data = None
        self.bar_data = self.prepare_bar_data()
        self.fxcm_conn.subscribe_market_data('EUR/USD', [self.on_prices_update])
        self.latest_tick_event = None
        self.continue_backtest = True
        self.bar_updated = False

    def prepare_bar_data(self):
        result = {}
        for s in self.symbol_list:
            fn = os.path.join(self.csv_dir, "%s.csv" % s)
            old_df = pd.read_csv(fn, header=0, index_col=0, names=['date',
                                                                   'bidopen',
                                                                   'bidclose',
                                                                   'bidhigh',
                                                                   'bidlow',
                                                                   'askopen',
                                                                   'askclose',
                                                                   'askhigh',
                                                                   'asklow',
                                                                   'tickqty'])
            # fxcm 最多能取 10000 根 k 线，m1 大概是 7 天的数据
            last_updated_dt = datetime.strptime(str(old_df.index[-1]), "%Y-%m-%d %H:%M:%S")
            print('API读取 1min的历史数据', datetime.now())
            new_df = self.fxcm_conn.get_candles(fxcm_symbol_from[s], period='m1',
                                                # 从上一次更新时间的下一分钟开始
                                                start=last_updated_dt + timedelta(minutes=1),
                                                # TODO: GMT 和 UTC 的转换
                                                end=datetime.now() - timedelta(hours=10))
            # .set_index('date')
            result[s] = pd.concat([old_df, new_df]).drop_duplicates()
            # Save to disk. need to do this in the end of session as well.
            result[s].to_csv(fn)
            print('结束，保存', datetime.now())
        return result

    # noinspection PyMethodMayBeStatic
    def create_fxcm_connection(self):
        """
        Connect to fxcm server.
        """
        print("开始链接")
        fxcm_conn = fxcmpy(config_file='fxcm.cfg', server='demo')
        print("链接成功", datetime.now() - timedelta(hours=10))
        # 竟然是自动链接的？
        return fxcm_conn

    def save_data(self):
        print('Saving data.')
        for s in self.symbol_list:
            fn = os.path.join(self.csv_dir, "%s.csv" % s)
            self.bar_data[s].to_csv(fn)
        fn = os.path.join(self.csv_dir, "%s_TICK.csv" % 'EUR_USD')
        self.tick_data.to_csv(fn)

    def disconnect(self):
        print("Disconnecting from fxcm.")
        # TODO: hardcoded EUR/USD
        self.fxcm_conn.unsubscribe_market_data('EUR/USD')
        self.save_data()
        self.fxcm_conn.close()
        print("Disconnected")

    # data:
    # 1 | EUR/USD | 2018-06-06 10:06:29.800000, 1.17725, 1.17749, 1.17756, 1.17095
    def on_prices_update(self, data, dataframe):
        # print('on_price_update', datetime.now())
        # 1. 把最新的 dataframe 的数据存储到当前类的一个属性里（TODO: 结束前记得存储回本地）
        self.tick_data = dataframe
        # 2. 更新最新的 tick event
        tick_event = self._create_event(data)
        # 3. 更新 bar data，如果有更新，新建一个 bar data 的事件
        # 使用收到的tick的时间，本地系统时间可能不准
        dt_str = str(self.bar_data['EUR_USD'].tail(1).index.values[0]).split('.')[0]
        bar_last_updated = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        # print(bar_last_updated)
        tick_dt_str = str(self.tick_data.tail(1).index.values[0]).split('.')[0]
        tick_last_updated = datetime.strptime(tick_dt_str, "%Y-%m-%dT%H:%M:%S")
        # print(tick_last_updated)
        if tick_last_updated - timedelta(minutes=1) >= bar_last_updated:
            print("=====")
            print("开始更新bar", datetime.now())
            cols = ['open', 'close', 'high', 'low']
            data_bid = self.tick_data['Bid'].resample('1Min').ohlc()[cols].add_prefix('bid')
            data_ask = self.tick_data['Ask'].resample('1Min').ohlc()[cols].add_prefix('ask')
            tick_data = pd.concat([data_bid, data_ask], axis=1)
            tick_data.index.name = 'date'
            # dt_str: '2020-05-25T03:46:00'
            # TODO: hardcoded EUR_USD should be EUR/USD mapped
            dt_str = str(self.bar_data['EUR_USD'].tail(1).index.values[0]).split('.')[0]
            bar_last_updated = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            # 只filter出上次更新到上一分钟的数据，理论上应该就一条数据
            tick_data = tick_data[(tick_data.index > bar_last_updated)].head(1)
            self.bar_data['EUR_USD'] = pd.concat([self.bar_data['EUR_USD'], tick_data]).drop_duplicates()
            self.bar_updated = True
            print('完成 Bar 的更新', datetime.now())
            print("=====")
        if self.latest_tick_event is not None:
            # 难道原因是这个速度太快？
            print("losing %s" % self.latest_tick_event)
        self.latest_tick_event = tick_event

    # noinspection PyMethodMayBeStatic
    def _create_event(self, data):
        symbol = data["Symbol"]
        update_time = pd.to_datetime(int(data['Updated']), unit='ms')
        bid = data['Rates'][0]
        ask = data['Rates'][1]
        return TickEvent(symbol, update_time, bid, ask)

    def stream_next(self):
        """
        Place the next PriceEvent (BarEvent or TickEvent) onto the event queue.
        """
        # print('我来要新的数据来了', datetime.now())
        if self.bar_updated:
            print('新的bar事件')
            self.events_queue.put(MarketEvent())
            self.bar_updated = False
        elif self.latest_tick_event is not None:
            # print('新的tick事件')
            self.events_queue.put(self.latest_tick_event)
            self.latest_tick_event = None

    def get_latest_bar_datetime(self, symbol):
        dt_str = str(self.bar_data[symbol].tail(1).index.values[0]).split('.')[0]
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

    def get_latest_bar_value(self, symbol, val_type):
        return self.bar_data[symbol].tail(1)[val_type].values[0]


if __name__ == '__main__':
    import queue, time
    events_queue = queue.Queue()
    end_datetime = datetime.now() + timedelta(minutes=8)
    data_handler = FXCMLiveTickDataHandler(events_queue, '../data/M1', ['EUR_USD'], end_datetime)
    execution_handler = FXCMExecutionHandler(events_queue, data_handler, end_datetime, data_handler.fxcm_conn)
    i = 0
    buy = True
    while _continue_loop_condition(data_handler):
        try:
            event = events_queue.get(False)
        except queue.Empty:
            data_handler.stream_next()
        except queue.Full:
            print("full")
        else:
            # print('有事件进来了', datetime.now())
            if event is not None:
                if event.type == 'MARKET':
                    print("新的MARKET事件", datetime.now())
                    # print(data_handler.get_latest_bar_datetime('EUR_USD'))
                    # print('Now is ', datetime.now())
                    # print('Data is')
                    # print(data_handler.bar_data['EUR_USD'].tail(1))
                    # print('bidclose is', data_handler.get_latest_bar_value('EUR_USD', 'bidclose'))
                    if buy:
                        print('生成订单：买')
                        signal = SignalEvent('EUR_USD', datetime.now(), 'LONG', 1000)
                        order = OrderEvent(signal, 1000, 'BUY')
                        events_queue.put(order)
                        buy = False
                    else:
                        print('生成订单：卖')
                        signal = SignalEvent('EUR_USD', datetime.now(), 'SHORT', 1000)
                        order = OrderEvent(signal, 1000, 'SELL')
                        events_queue.put(order)
                        buy = False
                elif event.type == 'TICK':
                    pass
                    # print('新的Tick事件', datetime.now())
                    # print(event)
                elif event.type == 'ORDER':
                    print('执行订单')
                    execution_handler.execute_order(event)
