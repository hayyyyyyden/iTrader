import queue
import time
from datetime import datetime

from data import HistoricCSVDataHandler
from strategy import BuyAndHoldStrategy
from portfolio import NaivePortfolio
from execution import SimulatedExecutionHandler

# Declare the components with respective parameters
events = queue.Queue()
bars = HistoricCSVDataHandler(events, './data', ['GBP_USD_D'])
strategy = BuyAndHoldStrategy(bars, events)
start_date = datetime(2019,12,11)
port = NaivePortfolio(bars, events, start_date)
broker = SimulatedExecutionHandler(events)

while True:
    # Update the bars (specific backtest code, as opposed to live trading)
    if bars.continue_backtest == True:
        bars.update_bars()
    else:
        break

    # Handle the events
    while True:
        try:
            event = events.get(False)
        except queue.Empty:
            break
        else:
            if event is not None:
                if event.type == 'MARKET':
                    strategy.calculate_signals(event)
                    port.update_timeindex(event)

                elif event.type == 'SIGNAL':
                    port.update_signal(event)

                elif event.type == 'ORDER':
                    broker.execute_order(event)

                elif event.type == 'FILL':
                    port.update_fill(event)

    # 10-Minute heartbeat
    time.sleep(0.01)

port.create_equity_curve_dataframe()
stats = port.output_summary_stats()
for s in port.all_positions:
    print(s)
# print(stats)
