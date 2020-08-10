#Hayden Yu 8/4/2020
#This is a program that finds buy/sell signals with MACD inspired by Computer Science from YouTube
#Plus CCI indicator and MACD Paper Trading

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

def MACD_trading(signal):
    #input amount
    print("Input capital:")
    cap = int(input())

    buy_price = []
    sell_price = []
    p_l = []
    shares = 0
    b_mkt_value = 0
    s_mkt_value = 0
    buy_flag = False
    for i in range(0, len(signal)):
        if not math.isnan(signal['MACD Buy'][i]): #buy at MACD buy
            if int(signal['MACD Buy'][i]) < cap and not buy_flag:
                buy_flag = True
                buy_price.append(int(signal['MACD Buy'][i]))
                shares = math.floor(cap/int(signal['MACD Buy'][i]))
                b_mkt_value = shares*int(signal['MACD Buy'][i])
                cap -= b_mkt_value
                #print("bought:")
                #print(shares, b_mkt_value, cap)
            else:
                print("not enough capital to Buy")
        elif not math.isnan(signal['MACD Sell'][i]): #sell at MACD sell
            if buy_flag:
                buy_flag = False
                sell_price.append(int(signal['MACD Sell'][i]))
                s_mkt_value = shares*int(signal['MACD Sell'][i])
                #calculate P&L
                cap += s_mkt_value
                p_l.append(s_mkt_value - b_mkt_value)
                #print("sold:")
                #print(shares, s_mkt_value, cap)
        else:
            continue
                
    return(buy_price, sell_price, p_l)

def main():
    #input Ticker here
    print("Input ticker(s)")
    ticker = input()
    ticker = ticker.split()
    for j in range (0, len(ticker)):
        plt.figure(figsize=(12.5, 4.5))
        plt.title(str(ticker[j]))
        ticker_name = yf.Ticker(ticker[j]) 
        ticker_his = ticker_name.history(period="1y", interval="1d") #duration of tickers history
        # tic_marketcap = int(dis.info["marketCap"])
        # tic_marketcap = round(tic_marketcap/1000000000)
        # print(str(dis_marketcap) + "b")
        shortEMA = ticker_his.Close.ewm(span=5, adjust=False).mean()
        longEMA = ticker_his.Close.ewm(span=35, adjust=False).mean()
        MACD = shortEMA-longEMA
        signal = MACD.ewm(span=5, adjust=False).mean()

        ticker_his['MACD'] = MACD
        ticker_his['Signal Line'] = signal

        a = MACD_indicator(ticker_his)
        ticker_his['MACD Buy'] = a[0]
        ticker_his['MACD Sell'] = a[1]

        #MACD plot
        # plt.plot(ticker_his.index, MACD, label="DIS MACD", color="red")
        # plt.plot(ticker_his.index, signal, label="Signal Line", color="blue")
        #plt.show()

        b = CCI_calculator(ticker_his, 35, 0.015)
        ticker_his['CCI value'] = b
        c = CCI_buy(ticker_his)
        ticker_his['CCI Buy'] = c

        #CCI plot
        # plt.plot(ticker_his.index, ticker_his['CCI value'], label="DIS CCI", color='black')
        # plt.axhline(y=-100, color="red", linestyle='dashed')
        #plt.show()

        print(str(ticker[j])+" strong buy date:")
        d = []
        for i in range(0, len(ticker_his)): #strong buy when CCI buy price = MACD buy price
            if math.isnan(ticker_his['MACD Buy'][i]) or math.isnan(ticker_his['CCI Buy'][i]):
                d.append(np.nan)
            elif ticker_his['MACD Buy'][i] == ticker_his['CCI Buy'][i]:
                d.append(ticker_his["Close"][i])
                print(ticker_his.index[i]) #date to buy
            else:
                d.append(np.nan)
        print('\n')
        ticker_his['Strong_Buy'] = d
        #print(ticker_his)

        #Buy-sell siganl plot
        plt.scatter(ticker_his.index, ticker_his['MACD Buy'], color='purple', label='MACD Buy', marker='^', alpha = 1)
        plt.scatter(ticker_his.index, ticker_his['MACD Sell'], color='red', label='MACD Sell', marker='v', alpha = 1)
        plt.scatter(ticker_his.index, ticker_his['CCI Buy'], color='blue', label='CCI Buy', marker='^', alpha = 1)
        not_nan = False
        for i in range(0, len(ticker_his['Strong_Buy'])):
            if math.isnan(ticker_his['Strong_Buy'][i]):
                continue
            else:
                not_nan = True
        if not_nan: #graph only if there's a strong buy
            plt.scatter(ticker_his.index, ticker_his['Strong_Buy'], color='green', label='Strong Buy', marker='^', alpha = 1)
       
        plt.plot(ticker_his["Close"], label = str(ticker[j]), alpha=0.35)
        plt.legend(loc='upper left')
        plt.xticks(rotation=45)

        #output MACD paper trading
        e = MACD_trading(ticker_his)
        df = pd.DataFrame(e)
        df = df.T
        df = df.rename(columns={0:'Buy price', 1:'Sell price', 2:'P&L'})
        print("Total P&L:")
        print(df['P&L'].sum())
        df.to_csv(ticker[j]+".csv", index_label='Trades')
        #print(df)
        plt.show()

if __name__ == "__main__":
    main()