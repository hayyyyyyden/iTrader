import datetime
import pprint
import queue
import time

class Backtest(object):
    """
    Enscapsulates the settings and components for carrying out an event-driven
    backtest.
    """

    def __init__(
        self, csv_dir, symbol_list, initial_capital, heartbeat, start_date,
        data_handler, execution_handler, portfolio, strategy
    ):
        """
        Initialises the backtest.

        Parameters:
        csv_dir - The hard root to the CSV data directory.
        symbol_list - The list of symbol strings.
        initial_capital - The starting capital for the portfolio.
        heartbeat - Backtest "heartbeat" in seconds.
        start_date - The start datetime of the strategy.
        data_handler - (Class) Handles the market data feed.
        execution_handler - (Class) Handles the orders/fills for traders.
        portfolio - (Class) Keeps track of portfolio current and prior
                    positions.
        strategy - (Class) Generates signals based on market data.
        """
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.heartbeat = heartbeat
        self.start_date = start_date

        self.data_handler_cls = data_handler
        self.execution_handler_cls = execution_handler
        self.portfolio_cls = portfolio
        self.strategy_cls = strategy

        self.events = queue.Queue()

        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1

        self._generate_trading_instances()

    def _generate_trading_instances(self):
        """
        Generates the trading instance objects from their class types.
        """
        print("Creating DataHandler, Strategy, Portfolio and ExecutionHandler")

        self.data_handler = self.data_handler_cls(self.events,
                                                  self.csv_dir,
                                                  self.symbol_list)
        self.strategy = self.strategy_cls(self.data_handler, self.events)
        self.portfolio = self.portfolio_cls(self.data_handler,
                                            self.events,
                                            self.start_date,
                                            self.initial_capital)
        self.execution_handler = self.execution_handler_cls(self.events,
                                                            self.data_handler)

    def _run_backtest(self):
        """
        Executes the backtest.
        """
        i = 0
        while True:
            i += 1
            print(i)
            # Update the market bars
            if self.data_handler.continue_backtest == True:
                self.data_handler.update_bars()
            else:
                # TODO: Close all open orders 关闭所有未平仓订单
                # e.g. self.execution_handler.clos_all_open_orders()
                break

            # Handle the events:
            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.type == 'MARKET':
                            fill_event = self.execution_handler.scan_open_orders(event)
                            if fill_event is not None:
                                self.portfolio.update_fill(fill_event)
                            self.strategy.calculate_signals(event)
                            self.portfolio.update_timeindex(event)

                        elif event.type == 'SIGNAL':
                            self.signals += 1
                            self.portfolio.update_signal(event)

                        elif event.type == 'ORDER':
                            self.orders += 1
                            self.execution_handler.execute_order(event)

                        elif event.type == 'FILL':
                            self.fills += 1
                            self.portfolio.update_fill(event)

            time.sleep(self.heartbeat)

    def _output_performance(self):
        """
        Outputs the strategy performance from the backtest.
        """
        self.portfolio.create_equity_curve_dataframe()
        self.portfolio.create_trade_history_dataframe()
        self.portfolio.create_order_history_dataframe()

        print("Creating summary stats...")
        stats = self.portfolio.output_summary_stats()

        print("Creating equity curve...")
        print(self.portfolio.equity_curve.tail(10))
        pprint.pprint(stats)

        print("Signals: %s" % self.signals)
        print("Orders: %s" % self.orders)
        print("Fills: %s" % len(self.portfolio.all_fills))

    def simulate_trading(self):
        """
        Simulate the backtest and outputs portfolio performance.
        """
        self._run_backtest()
        self._output_performance()