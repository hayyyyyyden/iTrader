<p align="center">
  <img src="https://github.com/hayyyyyyden/iTrader/blob/master/.github/logo.png?raw=true" alt="iTrader logo" width="100%">
</p>

<p align="center">

[![iTrader](https://github.com/hayyyyyyden/iTrader/blob/master/.github/badges/iTrader-hello-world-badge.svg?raw=true  "Run iTrader 'Hello, World!' without installing anything")](#iTrader-hello-world-)
[![iTrader Docs](https://github.com/hayyyyyyden/iTrader/blob/master/.github/badges/docs-badge.svg?raw=true  "Checkout our docs and learn iTrader")]()
[![Python 3.7 3.8](https://github.com/hayyyyyyden/iTrader/blob/master/.github/badges/python-badge.svg?raw=true  "iTrader supports Python 3.7 and above")]()
</p>

<p align="left">
  <a href="https://github.com/hayyyyyyden/iTrader">English</a> •
  <a href="https://github.com/hayyyyyyden/iTrader/blob/master/README.ja.md">日本語</a> •
  <a href="https://github.com/hayyyyyyden/iTrader/blob/master/README.zh.md">中文</a>
</p>

Want to test your new AI-integrated trading idea with your favourite python language? You come to the right place!

**iTrader** is *the* Python framework for inferring viability of trading strategies on both historical (past) data AND live data.

🧩 **Event-based Backtesting** - iTrader is completely event-driven, which leads to straightforward transitioning of strategies from a research phase to a live trading implementation.

🚀 **Supports All Types of Orders.** - iTrader Supports not only Market order, but also Limit BUY/SELL, Stop BUY/SELL. Easily bring your trading algorithm to the next level.

🤖 **Machine learning & Deep learning Made Easy** - Want to try the state-of-art AI in trading? As data scientists, we love that idea as well! Detailed AI trading demo strategies will help you get started in a minute.

🧡 **Powerful Extensions, Simple Integration** - New to trading in Forex or Stock? Simply write a Python class to express your idea, that's all you need to do. Plugging in new algorithms has never been that easy, as it should be. [Check out the tutorials](#iTrader-hello-world-) and find more examples.

iTrader is built upon the idea and code from [this series of tutorial articles](https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-I/) written by Dr. Michael L. Halls-Moore.

## Table of Contents

- [Install](#install)
- ["Hello, World!" 👋🌍](#hello-world-)

## Install

1. If you don't have `Python 3` installed on your Mac, install it first by running the following command:
```
brew install python3
```
2. Clone this repo using
```
git clone https://github.com/hayyyyyyden/iTrader.git
```
3. `cd iTrader/` into the root directory of this project you just downloaded, then use `pip` to install the requirements:
```
pip install -r requirements.txt
```
You're all set now.

## "Hello, World!" 👋🌍

In the root directory of iTrader, run the following python command:

```
python examples/volatility_autocorrelation.py
```

It should log output in the terminal like this:
```
Creating DataHandler, Strategy, Portfolio and ExecutionHandler
...
...
...
Creating summary stats...
[('Profit', '4990.9 pips.'),
 ('Annualized Sharpe Ratio', 'nan'),
 ('Max Drawdown', 'inf%'),
 ('Drawdown Duration', 'nan hours'),
 'Win rate 60.6%',
 'Trade number 944',
 'Total Profit 23390.9',
 'Total Loss -18400.0']
Creating equity curve...
```
Then a PnL curve for this strategy.


