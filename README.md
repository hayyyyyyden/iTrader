<p align="center">
  <img src="https://github.com/hayyyyyyden/iTrader/blob/master/.github/logo.png?raw=true" alt="iTrader logo" width="100%">
</p>

<p align="center">

[![iTrader](https://github.com/hayyyyyyden/iTrader/blob/master/.github/badges/iTrader-hello-world-badge.svg?raw=true  "Run iTrader 'Hello, World!' without installing anything")](#iTrader-hello-world-)
[![iTrader Docs](https://github.com/hayyyyyyden/iTrader/blob/master/.github/badges/docs-badge.svg?raw=true  "Checkout our docs and learn iTrader")]()
[![Python 3.7 3.8](https://github.com/hayyyyyyden/iTrader/blob/master/.github/badges/python-badge.svg?raw=true  "iTrader supports Python 3.7 and above")]()
</p>

<p align="center">
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
- [iTrader "Hello, World!" 👋🌍](#iTrader-hello-world-)
- [Getting Started](#getting-started)
- [Documentation](#documentation)
- [Tutorial](#tutorial)

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

## iTrader "Hello, World!" 👋🌍

In the root directory of iTrader, run the following python command:

```
python examples/volatility_autocorrelation.py
```

It should log output in the terminal like this:
```
Creating DataHandler, Strategy, Portfolio and ExecutionHandler
{'AUD_USD_H4': 0}
[{'AUD_USD_H4': 0, 'datetime': datetime.datetime(2015, 1, 1, 0, 0)}]
{'AUD_USD_H4': 0.0, 'cash': 10000, 'commission': 0.0, 'total': 10000}
[{'AUD_USD_H4': 0.0, 'datetime': datetime.datetime(2015, 1, 1, 0, 0), 'cash': 10000, 'commission': 0.0, 'total': 10000}]

......

<----- K 线时间 2015-05-08 09:00:00 -----> (当前实际时间是 2015-05-08 13:00:00 的第一秒)
过去 72 个小时, 最高价是 0.80306, 最低价是 0.78633. 波动值 R2 是 167.3 个 Pips.
当前 R2 波动值满足限制条件: 130 < R2 < 190 

过去 48 个小时, 最高价是 0.80306, 最低价是 0.78633. 波动值 R 是 167.3 个 Pips.
当前价格是 0.79389. 0.12 倍的 R 是 20.1 个 pips 
开一个限价的买单 (Limit Buy Order) 在当前价格 0.79389 的 20.1 个 pips 之下，即 0.79188.
目标盈利 ( profit_target ) 是 0.32 倍的 R，即 53.5 个 pips.
即, 0.79723
止损 (stop_loss) 为固定的 50 个 pips.
即, 0.78688
19

```

## Getting Started



## Documentation



## Tutorial

