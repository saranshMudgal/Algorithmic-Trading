# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 16:36:20 2021

@author: SARANSH
"""

import pandas as pd
import numpy as np
import yahoo_fin.stock_info as si

# stockList = ["RELIANCE","TCS","ITC","TATAMOTORS","ONGC"]
stockList = pd.read_csv('NIFTY_MIDSMALLCAP_400.csv')
stockList = stockList.iloc[1:3,[0]]
finRecord_cy = {}
finRecord_py = {}
finRecord_ppy = {}
stockRecord = {}

for stock in stockList['SYMBOL \n']:
  try:
    tempDir_cy = {} 
    tempDir_py = {}
    tempDir_ppy = {}
    temp_stats = {}
    ticker = stock + ".NS"
    
    print("Fetching Data for",stock)
    balanceSheet = si.get_balance_sheet(ticker)
    for index in balanceSheet.index:
        tempDir_cy[index] = balanceSheet.loc[index][0]
        tempDir_py[index] = balanceSheet.loc[index][1]
        tempDir_ppy[index] = balanceSheet.loc[index][2]
    
    incomeStatement = si.get_income_statement(ticker)
    for index in incomeStatement.index:
        tempDir_cy[index] = incomeStatement.loc[index][0]
        tempDir_py[index] = incomeStatement.loc[index][1]
        tempDir_ppy[index] = incomeStatement.loc[index][2]
        
    cashFlow = si.get_cash_flow(ticker)
    for index in cashFlow.index:
        tempDir_cy[index] = cashFlow.loc[index][0]
        tempDir_py[index] = cashFlow.loc[index][1]
        tempDir_ppy[index] = cashFlow.loc[index][2]
        
    stockStats = si.get_quote_data(ticker)
    for key in stockStats.keys():
        temp_stats[key] = stockStats[key]
        
    finRecord_cy[stock] = tempDir_cy
    finRecord_py[stock] = tempDir_py
    finRecord_ppy[stock] = tempDir_ppy
    stockRecord[stock] = temp_stats
  except:
      print("Problem fetching Data for ", stock)
    
finRecord_cy = pd.DataFrame(finRecord_cy)
finRecord_py = pd.DataFrame(finRecord_py)
finRecord_ppy = pd.DataFrame(finRecord_ppy)
stockRecord = pd.DataFrame(stockRecord)

finRecord_cy.dropna(axis=1,inplace=True,how="all")
finRecord_py.dropna(axis=1,inplace=True,how="all")        
finRecord_ppy.dropna(axis=1,inplace=True,how="all")   

def piotroski_score(cy,py,ppy):
    f_score = {}
    stockList = cy.columns
    for stock in stockList:
        ROA = int ( ( cy[stock]['netIncome'] / (cy[stock]['totalAssets'] + py[stock]['totalAssets'])/2 ) > 0 and 
                   ( py[stock]['netIncome'] / (py[stock]['totalAssets'] + ppy[stock]['totalAssets'])/2 ) > 0 )
        CFO = int( (cy[stock]['totalCashFromOperatingActivities'] > 0 and py[stock]['totalCashFromOperatingActivities'] 
                  and ppy[stock]['totalCashFromOperatingActivities'] >0 ) )
        ROA_comp = int( ( cy[stock]['netIncome'] / (cy[stock]['totalAssets'] + py[stock]['totalAssets'])/2 ) >= 
                       ( py[stock]['netIncome'] / (py[stock]['totalAssets'] + ppy[stock]['totalAssets'])/2 ) )
        CFO_ROA_comp = int ( ( cy[stock]['totalCashFromOperatingActivities'] / cy[stock]['totalAssets'] ) > 
                           ( cy[stock]['netIncome'] / (cy[stock]['totalAssets'] + py[stock]['totalAssets'])/2 ) )
        LTD = int( ( cy[stock]['longTermDebt'] < py[stock]['longTermDebt'] ) and 
                  (py[stock]['longTermDebt'] <= ppy[stock]['longTermDebt']) )
        CR = int( ( (cy[stock]['totalCurrentAssets'] / cy[stock]['totalCurrentLiabilities']) > (py[stock]['totalCurrentAssets'] / py[stock]['totalCurrentLiabilities']) ) and 
             ( (py[stock]['totalCurrentAssets'] / py[stock]['totalCurrentLiabilities']) > (ppy[stock]['totalCurrentAssets'] / ppy[stock]['totalCurrentLiabilities']) ) )
        dilution = int( ( cy[stock]['commonStock'] <= py[stock]['commonStock'] ) and ( py[stock]['commonStock'] <= ppy[stock]['commonStock'] ) )
        GPM = int( ( ( cy[stock]['grossProfit'] / cy[stock]['totalRevenue'] ) >= ( py[stock]['grossProfit'] / py[stock]['totalRevenue'] ) )
               and ( ( py[stock]['grossProfit'] / py[stock]['totalRevenue'] ) >= ( ppy[stock]['grossProfit'] / ppy[stock]['totalRevenue'] ) ) )
        ATO =  int( ( cy[stock]['netIncome'] / (cy[stock]['totalAssets'] + py[stock]['totalAssets'])/2 ) >=
               ( py[stock]['netIncome'] / (py[stock]['totalAssets'] + ppy[stock]['totalAssets'])/2 ) )
        f_score[stock] = [ROA,CFO,ROA_comp,CFO_ROA_comp,LTD,CR,dilution,GPM,ATO]
        
    f_score = pd.DataFrame(f_score)
    return f_score
    
report = piotroski_score(finRecord_cy, finRecord_py, finRecord_ppy)

valueStocks = []
# for stock in report.sum().sort_values(ascending=False).index[0:min(10,len(report.columns))]:
#     valueStocks.append(stock)
    
# print("The Companies with Strong Fundamentals are ", valueStocks)
# print(report['GESHIP'])

company = report.columns
for c in company :
    if(report[c].sum() >= 7):
        valueStocks.append(c)
    
print(valueStocks)