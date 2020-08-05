#Hayden Yu 8/4/2020
#This is a program that finds buy/sell signals with MACD inspired by Computer Science from YouTube

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

def CCI_calculator(signal, n, constant):
    TP = (signal['High']+signal['Low']+signal['Close'])/3
    CCI = pd.Series((TP-TP.rolling(n).mean())/(constant*TP.rolling(n).std()), name='CCI_'+str(n))
    return CCI

def CCI_buy(signal):
    Buy = []
    flag = -1

    for i in range(0, len(signal)):
        if math.isnan(signal['CCI value'][i]):
            Buy.append(np.nan)
        else:
            if int(signal['CCI value'][i]) > -100:
                if flag != 1:
                    Buy.append(signal['Close'][i])
                    flag = 1
                else:
                    Buy.append(np.nan)
            else:
                flag = -1
                Buy.append(np.nan)
    
    return Buy

def MACD_indicator(signal):
    Buy = []
    Sell = []
    flag = -1

    for i in range(0, len(signal)):
        if signal['MACD'][i] > signal['Signal Line'][i]: #when MACD value is above the Signal Line
            Sell.append(np.nan)
            if flag != 1: #first time MACD > Signal
                Buy.append(signal['Close'][i]) #buy price
                flag = 1
            else:
                Buy.append(np.nan)
        elif signal['MACD'][i] < signal['Signal Line'][i]: #when MACD value is below the Signal Line
            Buy.append(np.nan)
            if flag != 0: #first time MACD < Signal
                Sell.append(signal['Close'][i]) #sell price
                flag = 0
            else:
                Sell.append(np.nan)
        else:
            Buy.append(np.nan)
            Sell.append(np.nan)

    return (Buy, Sell)

plt.figure(figsize=(12.5, 4.5))
dis = yf.Ticker("UBER") #input Ticker here
dis_1mo = dis.history(period="1y", interval="1d")
# dis_marketcap = int(dis.info["marketCap"])
# dis_marketcap = round(dis_marketcap/1000000000)
#print(str(dis_marketcap) + "b")
#dis_1d = dis.history(period="1d", interval="1m")
shortEMA = dis_1mo.Close.ewm(span=5, adjust=False).mean()
longEMA = dis_1mo.Close.ewm(span=35, adjust=False).mean()
MACD = shortEMA-longEMA
signal = MACD.ewm(span=5, adjust=False).mean()

dis_1mo['MACD'] = MACD
dis_1mo['Signal Line'] = signal

a = MACD_indicator(dis_1mo)
dis_1mo['Buy_Signal_Price'] = a[0]
dis_1mo['Sell_Signal_Price'] = a[1]

b = CCI_calculator(dis_1mo, 30, 0.015)
dis_1mo['CCI value'] = b
c = CCI_buy(dis_1mo)
dis_1mo['CCI Buy'] = c
#print(dis_1mo)

#CCI plot
# plt.plot(dis_1mo.index, dis_1mo['CCI value'], label="DIS CCI", color='black')
# plt.axhline(y=-100, color="red", linestyle='dashed')


#MACD plot
# plt.plot(dis_1mo.index, MACD, label="DIS MACD", color="red")
# plt.plot(dis_1mo.index, signal, label="Signal Line", color="blue")

d = []
for i in range(0, len(dis_1mo)):
    if math.isnan(dis_1mo['Buy_Signal_Price'][i]) or math.isnan(dis_1mo['CCI Buy'][i]):
        d.append(np.nan)
    elif dis_1mo['Buy_Signal_Price'][i] == dis_1mo['CCI Buy'][i]:
        d.append(dis_1mo["Close"][i])
        print(dis_1mo.index[i]) #date to buy
    else:
        d.append(np.nan)

dis_1mo['Strong_Buy'] = d
#Buy-sell siganl plot
#plt.scatter(dis_1mo.index, dis_1mo['Buy_Signal_Price'], color='blue', label='MACD Buy', marker='^', alpha = 1)
plt.scatter(dis_1mo.index, dis_1mo['Sell_Signal_Price'], color='red', label='Sell', marker='v', alpha = 1)
#plt.scatter(dis_1mo.index, dis_1mo['CCI Buy'], color='blue', label='CCI Buy', marker='^', alpha = 1)
plt.scatter(dis_1mo.index, dis_1mo['Strong_Buy'], color='green', label='Strong Buy', marker='^', alpha = 1)
plt.plot(dis_1mo["Close"], label = "DIS", alpha=0.35)
plt.legend(loc='upper left')
plt.xticks(rotation=45)
plt.show()

