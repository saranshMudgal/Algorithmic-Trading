# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 11:22:01 2021

@author: SARANSH
"""

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import yahoo_fin.stock_info as si

# stockList = ["RELIANCE.NS"]
stockList = pd.read_csv('NIFTY_MIDSMALLCAP_400.csv')
# print(stockList['SYMBOL \n'])
stockList = stockList.iloc[1:400 ,[0]]
financialDir = {}

for ticker in stockList['SYMBOL \n']:
  try:
    tempDir = {}
    stock = ticker+".NS"
    print("Fetching Data for", stock)
    balanceSheet = si.get_balance_sheet(stock)
    for index in balanceSheet.index:
        tempDir[index] = balanceSheet.loc[index].mean(skipna=True)
    
    incomeStatement = si.get_income_statement(stock)
    for index in incomeStatement.index:
        tempDir[index] = incomeStatement.loc[index].mean(skipna=True)
        
    cashFlow = si.get_cash_flow(stock)
    for index in cashFlow.index:
        tempDir[index] = cashFlow.loc[index].mean(skipna=True)
        
    stockStats = si.get_quote_data(stock)
    for key in stockStats.keys():
        tempDir[key] = stockStats[key]
        
    financialDir[stock] = tempDir
    
  except:
    print("Problem getting Data for ", stock)
    

financialDf = pd.DataFrame(financialDir)
financialDf.dropna(axis=1,inplace=True,how="all")
stockList = financialDf.columns 

transposeDf = financialDf.transpose()
reportDf = pd.DataFrame()
reportDf['EBIT'] = transposeDf['ebit']
reportDf['TEV'] = transposeDf['marketCap'] + (-transposeDf['netBorrowings']) - (transposeDf['totalAssets'] - transposeDf['totalLiab'])
reportDf['Earning Yield'] = reportDf['EBIT']/reportDf['TEV']
reportDf['ROC'] = (transposeDf['ebit'])/(transposeDf['propertyPlantEquipment']+transposeDf['totalAssets']-transposeDf['totalLiab'])
    
reportDf['CombRank'] = reportDf['Earning Yield'].rank(ascending=False,na_option='bottom') + reportDf['ROC'].rank(ascending=False,na_option='bottom')
reportDf['Greenblats_Rank'] = reportDf['CombRank'].rank(method='first')
valueStocks = []

for stock in reportDf['Greenblats_Rank'].sort_values().index[0:min(25,len(reportDf['Greenblats_Rank']))]  : 
    valueStocks.append(stock)
    
print("The Fundamentally Strong Companies for Sound Investments are :-" , valueStocks)
      

