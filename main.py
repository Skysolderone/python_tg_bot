from  binance.client import Client
from binance.exceptions import BinanceAPIException
import dotenv
import os
import pandas as pd
from get_csv.csvdata import Csv


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
    df15m['ema5']=df15m['close'].rolling(window=5).mean()
 
    #anthor get binance kline data save to csv 00:00
    #concat kline data
    #load indicator
    #check indicator
    #run buy|sell

if __name__=='__main__':
    main()