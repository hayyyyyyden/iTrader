from datetime import datetime

from core.event import FillEvent, OrderEvent
from fxcmpy import fxcmpy

from core.execution import ExecutionHandler

fxcm_symbol_from = {
    'AUD_USD': 'AUD/USD',
    'EUR_USD': 'EUR/USD'
}


class FXCMExecutionHandler(ExecutionHandler):
    """
    Handles order execution via the FXCM Brokers API,
    for use against accounts when trading live directly.
    """

    def __init__(self, events_queue, bars, end_datetime, fxcm_conn=None):
        """
        Initialises the handler, setting the event queue
        as well as access to local data handler.

        Parameters:
        events_queue - The Queue of Event objects.
        """
        self.events_queue = events_queue
        self.bars = bars
        if fxcm_conn:
            self.fxcm_conn = fxcm_conn
        else:
            self.fxcm_conn = self.create_fxcm_connection()
        self.end_datetime = end_datetime
        self.all_orders = []

    def _find_open_order(self, symbol):
        # 找到当前所有订单中还开放的订单，即 entry_price 不是 None，
        # 但是 exit_price 是 None，返回。找不到返回 None。
        for order in self.all_orders:
            if order.symbol == symbol and order.entry_price is not None and order.exit_price is None:
                return order
        return None

    # noinspection PyMethodMayBeStatic
    def create_fxcm_connection(self):
        """
        Connect to fxcm server.
        """
        print("开始链接，时间:", datetime.now())
        fxcm_conn = fxcmpy(config_file='fxcm.cfg', server='demo')
        print("链接成功，时间:", datetime.now() - timedelta(hours=10))
        return fxcm_conn

    def execute_order(self, event):
        """
        Converts OrderEvents into FillEvents ,
        assume the fxcm account is a non hedging account, 不能同时开多和空
        Parameters:
        event - An Event object with order information.
        it can get fill price but not very well tested
        """

        if event.type == 'ORDER':
            # Now we are opening a new order 按照市场价开新单
            timeindex = self.bars.get_latest_bar_datetime(event.symbol)
            price = self.bars.get_latest_bar_value(event.symbol, "bidclose")
            order = self._find_open_order(event.symbol)
            if order is None:
                # 找不到，新建一个 order，更新它的进场时间和价格
                order = event
                order.entry_time = timeindex
                order.entry_price = price
                self.all_orders.append(event)
            else:
                # 找到了现有 order，更新它的信息
                order.exit_time = timeindex
                order.exit_price = price
                order.profit = (price - order.entry_price) * order.quantity
            # 无论如何，这个订单要按照市场价执行。
            # TODO: hardcoded ERU/USD
            print('执行订单', datetime.now())
            if event.direction == 'SELL':
                order = self.fxcm_conn.open_trade(symbol=fxcm_symbol_from[event.symbol],
                                          is_buy=False,
                                          amount=event.quantity,
                                          time_in_force='FOK',
                                          order_type='AtMarket',
                                          rate=0,
                                          is_in_pips=False,
                                          limit=event.profit_target,
                                          at_market=0,
                                          stop=event.stop_loss,
                                          trailing_step=None,
                                          account_id=None)
                print(event.profit_target)
                print(event.stop_loss)
                print(order)
            else:
                print(event.profit_target)
                print(event.stop_loss)
                order = self.fxcm_conn.open_trade(symbol=fxcm_symbol_from[event.symbol],
                                          is_buy=True,
                                          amount=event.quantity,
                                          time_in_force='FOK',
                                          order_type='AtMarket',
                                          rate=0,
                                          is_in_pips=False,
                                          limit=event.profit_target,
                                          at_market=0,
                                          stop=event.stop_loss,
                                          trailing_step=None,
                                          account_id=None)
                print(order)
            fill_event = FillEvent(order, timeindex, price,
                                   event.symbol, 'FXCM', event.quantity,
                                   event.direction)
            self.events_queue.put(fill_event)
