from  binance.client import Client
from binance.exceptions import BinanceAPIException
import dotenv
import os
import pandas as pd
import ta.momentum
import ta.volatility
from get_csv.csvdata import Csv
import ta

def main():
    print("init bot")
    dotenv.load_dotenv()
    #binance client init 
    apikey=os.getenv('apikey')
    secret=os.getenv('secret')
    client=Client(apikey,secret)
    Csv().getKline(client)
    
   
    try:
        result=client.get_account_api_permissions(recvWindow=10000)
    except BinanceAPIException as e:
        print(e)
    else:  
        print(result)
    
   
    #websocket connect 

    #read local 15m 30m 1h 2h 4h 1d csv
    pd15m=pd.read_csv('csv/15m.csv')
    pd30m=pd.read_csv('csv/30m.csv')
    pd1h=pd.read_csv('csv/1h.csv')
    pd2h=pd.read_csv('csv/2h.csv')
    pd4h=pd.read_csv('csv/4h.csv')
    pd1d=pd.read_csv('csv/1d.csv')

    df15m=pd.DataFrame(pd15m)
    df30m=pd.DataFrame(pd30m)
    df1h=pd.DataFrame(pd1h)
    df2h=pd.DataFrame(pd2h)
    df4h=pd.DataFrame(pd4h)
    df1d=pd.DataFrame(pd1d)
    df15m=add_indicator(df15m)
    df30m=add_indicator(df30m)
    df1h=add_indicator(df1h)
    df2h=add_indicator(df2h)
    df4h=add_indicator(df4h)
    df1d=add_indicator(df1d)
 
    #anthor get binance kline data save to csv 00:00
    #concat kline data
    #load indicator
    #check indicator
    #run buy|sell



def add_indicator(df):
    df['EMA_9']=df['close'].ewm(span=9,adjust=False).mean()
    df['EMA_21']=df['close'].ewm(span=21,adjust=False).mean()
    df['SMA_20']=df['close'].rolling(window=20).mean()
    df['SMA_50']=df['close'].rolling(window=50).mean()
    df['RSI_14']=ta.momentum.RSIIndicator(close=df['close'],window=14).rsi()
    df['ATR_14']=ta.volatility.AverageTrueRange(high=df['high'],low=df['low'],close=df['close'],window=14).average_true_range()
   
    return df



if __name__=='__main__':
    main()
