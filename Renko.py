# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 18:42:48 2021

@author: SARANSH
"""

import copy

import numpy as np
import pandas_datareader as pdr
import datetime as dt
import pandas as pd
from stocktrends import Renko
import statistics

def CAGR(DF):
    "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
    df = DF.copy()
    df["cum_return"] = (1 + df["ret"]).cumprod()

    CAGR = (df["cum_return"].tolist()[-1]) ** (1 / 10) - 1
    return CAGR

def ATR(DF, n):
    df = DF.copy()
    df['H-L'] = abs(df["High"] - df["Low"])
    df['H-PC'] = abs(df["High"] - df["Adj Close"].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Adj Close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    df.drop(['H-L', 'H-PC', 'L-PC'], inplace=True, axis=1)
    return df

pd.options.mode.chained_assignment = None

def renko_df(DF):
    df = DF.copy()
    df.reset_index(inplace=True)
    df = df.iloc[:, [0, 1, 2, 3, 4, 5]]
    df.columns = ["date", "high", "low", "open", "close", "volume"]
    df2 = Renko(df)
    df2.brick_size = ATR(DF, 14)["ATR"].mean()
    df_renko = df2.get_ohlc_data()

    df_renko["bar_num"] = np.where(df_renko["uptrend"] == True, 1, np.where(df_renko["uptrend"] == False, -1, 0))

    for i in range(1, len(df_renko["bar_num"])):
        if df_renko['bar_num'][i] > 0 and df_renko['bar_num'][i - 1] > 0:
            df_renko['bar_num'][i] = df_renko['bar_num'][i - 1] + df_renko['bar_num'][i - 1]
        elif df_renko['bar_num'][i] < 0 and df_renko['bar_num'][i - 1] < 0:
            df_renko['bar_num'][i] = df_renko['bar_num'][i - 1] + df_renko['bar_num'][i - 1]

    df_renko.drop_duplicates(subset='date', keep='last', inplace=True)

    return df_renko


# stockList = ["IOC.NS", "RELIANCE.NS", "BPCL.NS", "SBIN.NS", "HINDPETRO.NS", "ONGC.NS", "TATAMOTORS.NS",
#              "TATASTEEL.NS", "HINDALCO.NS", "ICICIBANK.NS", "NTPC.NS", "BHARTIARTL.NS", "COALINDIA.NS",
#              "LT.NS", "SAIL.NS", "BHEL.NS", "MARUTI.NS", "TCS.NS", "GAIL.NS"]
# # stockList = ["RELIANCE.NS"]
stockList = pd.read_csv("nifty50.csv")
stockList = stockList.iloc[1:,[0]]
stockList = stockList["Symbol"].tolist()

stockData = {}
endDate = dt.date.today()
startDate = dt.date.today() - dt.timedelta(365 * 10)
completed = []

for stock in stockList:
    attempt = 1
    while (stock not in completed) & (attempt <= 3):
        try:
            print("Fetching Data for ",stock)
            data = pdr.get_data_yahoo(stock+".NS", startDate, endDate)
            stockData[stock] = data
            completed.append(stock)
        except:
            print("Error fetching data for ", stock)
            attempt = attempt + 1



stockListFinal = stockData.keys()
ohlc_renko = {}
stockData_copy = copy.deepcopy(stockData)
tickerSignal = {}
tickerReturns = {}

for stock in stockListFinal:
    renkoDf = renko_df(stockData_copy[stock])
    renkoDf.columns = ['Date', 'open', 'high', 'low', 'close', 'uptrend', 'bar_num']
    stockData_copy[stock]['Date'] = stockData_copy[stock].index
    stockData_copy[stock].reset_index(drop=True, inplace=True)
    ohlc_renko[stock] = stockData_copy[stock].merge(renkoDf.loc[:, ['Date', 'bar_num']], how="outer", on='Date')
    ohlc_renko[stock]["bar_num"].fillna(method='ffill', inplace=True)
    tickerSignal[stock] = ""
    tickerReturns[stock] = []
    # print(ohlc_renko[stock].columns)


stockCAGR = []
for stock in stockListFinal:
    print("Calculating Returns for ", stock)
    for i in range(len(ohlc_renko[stock])):
        if tickerSignal[stock] == "":
            tickerReturns[stock].append(0)
            if ohlc_renko[stock]['bar_num'][i]>2:
                tickerSignal[stock] = "Buy"
            elif ohlc_renko[stock]['bar_num'][i] < -2:
                tickerSignal[stock] = "Sell"

        elif tickerSignal[stock] == "Buy":
            tickerReturns[stock].append((ohlc_renko[stock]['Adj Close'][i]/ohlc_renko[stock]['Adj Close'][i - 1]) - 1)
            if ohlc_renko[stock]['bar_num'][i] < -2:
                tickerSignal[stock] = "Sell"
            elif ohlc_renko[stock]['bar_num'][i] < 2:
                tickerSignal[stock] = ""

        elif tickerSignal[stock] == "Sell":
            tickerReturns[stock].append((ohlc_renko[stock]['Adj Close'][i - 1]/ohlc_renko[stock]['Adj Close'][i]) - 1)
            if ohlc_renko[stock]['bar_num'][i] > 2:
                tickerSignal[stock] = "Buy"
            elif (ohlc_renko[stock]['bar_num'][i] > -2):
                tickerSignal[stock] = ""

    ohlc_renko[stock]['ret'] = np.array(tickerReturns[stock])
    print(CAGR(ohlc_renko[stock]),stock)
    stockCAGR.append(CAGR(ohlc_renko[stock]))

stockCAGR.sort()





