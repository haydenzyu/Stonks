#Hayden Yu 8/4/2020
#This is a program that finds buy/sell signals with MACD inspired by Computer Science from YouTube

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def buy_sell(signal):
    Buy = []
    Sell = []
    flag = -1

    for i in range(0, len(signal)):
        if signal['MACD'][i] > signal['Signal Line'][i]:
            Sell.append(np.nan)
            if flag != 1:
                Buy.append(signal['Close'][i])
                flag = 1
            else:
                Buy.append(np.nan)
        elif signal['MACD'][i] < signal['Signal Line'][i]:
            Buy.append(np.nan)
            if flag != 0:
                Sell.append(signal['Close'][i])
                flag = 0
            else:
                Sell.append(np.nan)
        else:
            Buy.append(np.nan)
            Sell.append(np.nan)

    return (Buy, Sell)

plt.figure(figsize=(12.5, 4.5))
dis = yf.Ticker("DIS")
dis_1mo = dis.history(period="1y", interval="1d")
# dis_marketcap = int(dis.info["marketCap"])
# dis_marketcap = round(dis_marketcap/1000000000)
#print(str(dis_marketcap) + "b")
#dis_1d = dis.history(period="1d", interval="1m")
shortEMA = dis_1mo.Close.ewm(span=5, adjust=False).mean()
longEMA = dis_1mo.Close.ewm(span=30, adjust=False).mean()
MACD = shortEMA-longEMA
signal = MACD.ewm(span=5, adjust=False).mean()

dis_1mo['MACD'] = MACD
dis_1mo['Signal Line'] = signal

a = buy_sell(dis_1mo)
dis_1mo['Buy_Signal_Price'] = a[0]
dis_1mo['Sell_Signal_Price'] = a[1]

#print(dis_1mo)

#MACD plot
# plt.plot(dis_1mo.index, MACD, label="DIS MACD", color="red", alpha=0.35)
# plt.plot(dis_1mo.index, signal, label="Signal Line", color="blue", alpha=0.35)

#Buy-sell siganl plot
plt.scatter(dis_1mo.index, dis_1mo['Buy_Signal_Price'], color='green', label='Buy', marker='^', alpha = 1)
plt.scatter(dis_1mo.index, dis_1mo['Sell_Signal_Price'], color='red', label='Sell', marker='v', alpha = 1)
plt.plot(dis_1mo["Close"], label = "DIS", alpha=0.35)
plt.legend(loc='upper left')
plt.xticks(rotation=45)
plt.show()

