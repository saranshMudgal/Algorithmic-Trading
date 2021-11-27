# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 23:29:03 2021

@author: SARANSH
"""
# Importing the required Libraries
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta

#Importing the Dataset for both the Stocks
ticker_A = pd.read_csv('Stock_A_Price.csv')
ticker_B = pd.read_csv('Stock_B_Price.csv')

# Creating lists to store the Order Details of transactions in Stock B
buy_time = []
buy_price = []
sell_time = []
sell_price = []

# Function initiates order in Stock B
def createOrder(time, direction, ticker_B_copy):
    #Based on direction of the Trade, function is executed
     if(direction=="Long"):
         #Creating 'Long' at ith instance, and 'Long Unwinding' at (i+1)th instance
         buy_time.append(ticker_B_copy[ticker_B_copy['timestamp'] >= time].iloc[0,0])
         buy_price.append(ticker_B_copy[ticker_B_copy['timestamp'] >= time].iloc[0,1])
         sell_time.append(ticker_B_copy[ticker_B_copy['timestamp'] >= time].iloc[1,0])
         sell_price.append(ticker_B_copy[ticker_B_copy['timestamp'] >= time].iloc[1,1])
     elif (direction=="Short"):
         #Creating 'Short' at ith instance, and 'Short Covering' at (i+1)th instance
         sell_time.append(ticker_B_copy[ticker_B_copy['timestamp'] >= time].iloc[0,0])
         sell_price.append(ticker_B_copy[ticker_B_copy['timestamp'] >= time].iloc[0,1])
         buy_time.append(ticker_B_copy[ticker_B_copy['timestamp'] >= time].iloc[1,0])
         buy_price.append(ticker_B_copy[ticker_B_copy['timestamp'] >= time].iloc[1,1])
    
# Function monitors movements of Stock A and gives trade signal
def track_A(ticker_A, ticker_B, timelag, priceChangeForOrderTrigger):
    # Copying the Original dataset to a local variable to avoid making changes to original dataset
    ticker_A_copy = ticker_A.copy() 
    
    
    # Column Price Change stores difference in consecutive prices
    ticker_A_copy['Price Change'] = ticker_A_copy['price'].diff()\
        
    #Converting 'timestamp' from string format to datetime format 
    ticker_A_copy['timestamp'] = pd.to_datetime(ticker_A_copy['timestamp'])
    
    #Trimming dataset to store only the values where 'Price Change' >= priceChangeForOrderTrigger
    ticker_A_copy = ticker_A_copy[(ticker_A_copy['Price Change'] >= priceChangeForOrderTrigger) | (ticker_A_copy['Price Change'] <= -abs(priceChangeForOrderTrigger)) ]
    
    ticker_B_copy = ticker_B.copy()
    ticker_B_copy['timestamp'] = pd.to_datetime(ticker_B_copy['timestamp'])
    
    
    for i in range(0,ticker_A_copy.shape[0]):
        #Deciding the nature of the trade based on the price change of Stock A
        if(ticker_A_copy.iloc[i,2] < 0):
            direction = "Long"
        else :
            direction = "Short"
        
        # Order triggered in Stock B by including the timelag 
        createOrder(ticker_A_copy.iloc[i,0]+timedelta(milliseconds=timelag),direction, ticker_B_copy)

 #Calling the Function with timelag = 40 milliseconds (given) and priceChangeForOrderTrigger = 4.0 (given) 
track_A(ticker_A, ticker_B, 40, 4)

# Dataframe to store the detials of all executed order
order_history = pd.DataFrame(list(zip(buy_time, buy_price, sell_time, sell_price)),
                             columns=['Buy Time','Buy Price','Sell Time', 'Sell Price'])

#Stores the Profit/Loss of every trade
order_history['Difference'] = order_history['Sell Price'] - order_history['Buy Price']

#Summing the Profit/Loss from every trade to obtain Net Profit/Loss
print('The Profit from this Strategy is : ', order_history['Difference'].sum())