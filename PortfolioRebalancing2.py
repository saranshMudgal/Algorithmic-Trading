# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 17:15:22 2021

@author: SARANSH
"""

import numpy as np

import datetime as dt
import pandas as pd

from pandas_datareader import data as pdr


# data = pdr.get_data_yahoo('TCS.NS')

# stockList = ["IOC.NS", "RELIANCE.NS", "BPCL.NS", "SBIN.NS", "HINDPETRO.NS", "ONGC.NS", "TATAMOTORS.NS",
#              "TATASTEEL.NS", "HINDALCO.NS", "ICICIBANK.NS", "NTPC.NS", "BHARTIARTL.NS", "COALINDIA.NS",
#              "LT.NS", "SAIL.NS", "BHEL.NS", "MRPL.NS", "MARUTI.NS", "TCS.NS", "GAIL.NS", "CHENNPETRO.NS"]

stockList = pd.read_csv("nifty50.csv")
stockList = stockList.iloc[1:,[0]]
stockList = stockList["Symbol"].tolist()


stockData = {}
endDate = dt.date.today()
startDate = dt.date.today() - dt.timedelta(365 * 10)
completed = []

for stock in stockList:
    attempt = 1
    ticker = stock+".NS"
    while (stock not in completed) & (attempt <= 3):
        try:
            print("Fetching data for ",ticker)
            data = pdr.get_data_yahoo(ticker, startDate, endDate, interval='m')
            stockData[stock] = data
            completed.append(stock)
        except:
            print("Error fetching data for " + stock)
            attempt = attempt + 1

stockList = stockData.keys()

stockReturns = pd.DataFrame()
for stock in stockList:
    print("Calculating monthly returns for " + stock)
    stockData[stock]["Monthly returns"] = stockData[stock]["Adj Close"].pct_change()
    stockReturns[stock] = stockData[stock]["Monthly returns"]



def portfolioBalance(DF, n):
    df = DF.copy()
    portfolio = []
    month_returns = [0]
    for i in range(1, len(df)):
        if len(portfolio) > 0:
            month_returns.append(df[portfolio].iloc[i, :].mean())
            badPicks = df[portfolio].iloc[i].sort_values(ascending=True)[:int(n / 2)].index.values.tolist()
            portfolio = [stock for stock in portfolio if stock not in badPicks]

        required = n - len(portfolio)
        newPicks = df[stockList].iloc[i].sort_values(ascending=False)[:required].index.values.tolist()
        portfolio = portfolio + newPicks
        # print(portfolio)
    month_returns_dt = pd.DataFrame();
    month_returns_dt["Month Returns"] = np.array(month_returns)
    return month_returns_dt



def CAGR(DF):
    df = DF.copy()
    df["Cumulative Return"] = (1 + df["Month Returns"]).cumprod()
    answer = ((df["Cumulative Return"].iloc[-1]) ** (1 / 10)) - 1
    return answer * 100

def Volatility(DF):
    df = DF.copy()
    answer = df["Month Returns"].std() * np.sqrt(12)
    return answer*100

def Sharpe(DF,rf):
    df = DF.copy()
    sharpeRatio = ( CAGR(df) - rf )/Volatility(df)
    return sharpeRatio

def max_dd(DF):
   
    df = DF.copy()
    
    df["cum_return"] = (1 + df["Month Returns"]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd*100




print(CAGR(portfolioBalance(stockReturns, 6)))
print(Volatility(portfolioBalance(stockReturns,6)))
print(Sharpe(portfolioBalance(stockReturns,6),6.2))
print(max_dd(portfolioBalance(stockReturns, 6)))

