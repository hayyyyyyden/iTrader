import pprint
import queue
import time
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
from pathlib import Path
from csv import DictWriter

class Backtest(object):
    """
    Enscapsulates the settings and components for carrying out an event-driven
    backtest.
    """

    def __init__(
        self, csv_dir, symbol_list, initial_capital, heartbeat, start_date,
        data_handler, execution_handler, portfolio, strategy, kwargs=None
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
        self.kwargs = kwargs

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
        self.strategy = self.strategy_cls(self.data_handler, self.events, **self.kwargs)
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
                            fill_events = self.execution_handler.scan_open_orders(event)
                            if fill_events:
                                self.fills += len(fill_events)
                                self.portfolio.update_fills(fill_events)
                            self.strategy.calculate_signals(event)
                            self.portfolio.update_timeindex(event)

                        elif event.type == 'SIGNAL':
                            self.signals += 1
                            self.portfolio.update_signal(event)

                        elif event.type == 'ORDER':
                            self.orders += 1
                            self.execution_handler.execute_order(event)

                        elif event.type == 'ACTION':
                            self.execution_handler.execute_action(event)

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
        pprint.pprint(stats)

        print("Creating equity curve...")
        # Plot the equity curve
        fig = plt.figure()

        # Set the outer colour to white
        fig.patch.set_facecolor('white')

        ax1 = fig.add_subplot(211, ylabel='Portfolio value, %')
        self.portfolio.equity_curve['equity_curve'].plot(ax=ax1, color="blue", lw=2.)
        plt.grid(True)
        plt.tight_layout()

        # Temp implementation
        # TODO: refactor

        symbol = self.symbol_list[0]

        # Plot the returns
        ax2 = fig.add_subplot(212, ylabel='{} close price'.format(symbol))
        self.data_handler.raw_data[symbol]['close'].plot(ax=ax2, color="black", lw=2.)

        # TODO: this may crash, need to make a formal short_cut name
        s_name = self.strategy_cls.__name__[:3]
        dt_string = datetime.now().strftime("%m%d_%H%M")
        para_str = ''
        for key in self.kwargs:
            para_str += '_'
            para_str += key
            para_str += '_'
            para_str += str(self.kwargs[key])
        fd_name = "{}_{}{}".format(s_name, dt_string, para_str)
        Path("./results/{}".format(fd_name)).mkdir(parents=True, exist_ok=True)

        fig.savefig('./results/{}/PnL.png'.format(fd_name), dpi=100)
        self.portfolio.equity_curve.to_csv('./results/{}/equity.csv'.format(fd_name))
        self.portfolio.trade_history.to_csv('./results/{}/all_positions.csv'.format(fd_name))
        self.portfolio.order_history.to_csv('./results/{}/all_orders.csv'.format(fd_name))
        pd.DataFrame(self.portfolio.all_fills).to_csv('./results/{}/all_fills.csv'.format(fd_name))

        field_names = list(self.kwargs.keys()) + ['Profit', 'Sharpe', 'Max_Drawdown', 'Drawdown_Duration', 'Win_Rate',
                                                  'Trade_No', 'Total_Profit', 'Total_Loss', 'Folder_Name',
                                                  'Profit_Factor']
        stats.update(self.kwargs)
        stats.update({'Folder_Name': fd_name})
        self.append_dict_as_row('./results/{}_stats.csv'.format(s_name), stats, field_names)

        plt.show()

    @staticmethod
    def append_dict_as_row(file_name, dict_of_elem, field_names):
        # Open file in append mode
        with open(file_name, 'a+', newline='') as write_obj:
            # Create a writer object from csv module
            dict_writer = DictWriter(write_obj, fieldnames=field_names)
            # Add dictionary as wor in the csv
            dict_writer.writerow(dict_of_elem)

    def simulate_trading(self):
        """
        Simulate the backtest and outputs portfolio performance.
        """
        self._run_backtest()
        self._output_performance()
