from  binance.client import Client
from binance.exceptions import BinanceAPIException
import dotenv
import os
import pandas as pd
import ta.momentum
import ta.volatility
from get_csv.csvdata import Csv
import ta

position=0
price=0.00
side=''
totalBalance=0.00
totalpnl=0
def main():
    dotenv.load_dotenv()
    #binance client init 
    print('client init')
    apikey=os.getenv('apikey')
    secret=os.getenv('secret')
    client=Client(apikey,secret)

    #anthor get binance kline data save to csv 00:00
    Csv().getKline(client)
    
    #ps.Todo
    # try:
    #     result=client.get_account_api_permissions(recvWindow=10000)
    # except BinanceAPIException as e:
    #     print(e)
    # else:  
    #     print(result)
    
   
    #websocket connect 

    #read local 15m 30m 1h 2h 4h 1d csv
    print('load csv')
    pd15m=pd.read_csv('csv/15m.csv')
    pd30m=pd.read_csv('csv/30m.csv')
    pd1h=pd.read_csv('csv/1h.csv')
    pd2h=pd.read_csv('csv/2h.csv')
    pd4h=pd.read_csv('csv/4h.csv')
    pd1d=pd.read_csv('csv/1d.csv')

   
    
   
    #concat kline data
    unique15m=pd15m.drop_duplicates(subset='timestamp')
    unique15m=unique15m.sort_values(by=['timestamp']).reset_index(drop=True)
    unique30m=pd30m.drop_duplicates(subset='timestamp')
    unique30m=unique30m.sort_values(by=['timestamp']).reset_index(drop=True)
    unique1h=pd1h.drop_duplicates(subset='timestamp')
    unique1h=unique1h.sort_values(by=['timestamp']).reset_index(drop=True)
    unique2h=pd2h.drop_duplicates(subset='timestamp')
    unique2h=unique2h.sort_values(by=['timestamp']).reset_index(drop=True)
    unique4h=pd4h.drop_duplicates(subset='timestamp')
    unique4h=unique4h.sort_values(by=['timestamp']).reset_index(drop=True)
    unique1d=pd1d.drop_duplicates(subset='timestamp')
    unique1d=unique1d.sort_values(by=['timestamp']).reset_index(drop=True)
    arr={}

    #load indicator
    print('load indicator')
    df15m=add_indicator(unique15m)
    arr['15m']=df15m
    df30m=add_indicator(unique30m)
    arr['30m']=df30m
    df1h=add_indicator(unique1h)
    arr['1h']=df1h
    df2h=add_indicator(unique2h)
    arr['2h']=df2h
    df4h=add_indicator(unique4h)
    arr['4h']=df4h
    df1d=add_indicator(unique1d)
    arr['1d']=df1d
      
    for i,v in arr.items():
        #check indicator  buy|sell
        buy,sell=generate_signals(v)  
        change=pd.DataFrame()
        change=pd.concat([buy,sell])
        change=change.sort_values(by=['timestamp']).reset_index(drop=True)
        #check pnl
        pnl=runCheckPnl(change)
        print(f'{i}:{pnl}')


def runCheckPnl(change):
    global totalpnl
    side=''
    for index,v in change.iterrows():
        if v['RSI_14']<=30:
            if side=='':
                position=2
                side='long'
                totalBalance=position*v['close']
                pnl=0
                time=v['timestamp']
                #print(f'多单买入:{time}-{price}-{position}-{totalBalance}-{side}')
            if side=='long':
                position=position+2
                totalBalance=totalBalance+v['close']*2
                price=totalBalance/4
                pnl=0
                time=v['timestamp']     
                #print(f'多单补仓:{time}-{price}-{position}-{totalBalance}-{side}')

            if side=='short':
                price=v['close']
                sellbalance=price*position
                pnl=sellbalance-totalBalance
                side=''
                if pnl<0:
                    totalpnl=totalpnl-pnl
                else :
                     totalpnl=totalpnl+pnl
                time=v['timestamp']
                #print(f'空单平仓:{time}-{price}-{position}-{totalBalance}-{side}-{pnl}')
        if v['RSI_14']>=70:
            if side=='':
                position=2
                side='short'
                totalBalance=position*v['close']
                price=v['close']
                pnl=0
                time=v['timestamp']
                #print(f'空单开仓:{time}-{price}-{position}-{totalBalance}-{side}')
            if side=='long':
                price=v['close']
                sellbalance=price*position
                pnl=sellbalance-totalBalance
                side=''
                totalpnl=totalpnl+pnl
                time=v['timestamp']
                #print(f'多单平仓:{time}-{price}-{position}-{totalBalance}-{side}-{pnl}')
            if side=='short':
                position=position+2
                totalBalance=totalBalance+v['close']*2
                price=totalBalance/4
                pnl=0
                time=v['timestamp']
                #print(f'空单补仓:{time}-{price}-{position}-{totalBalance}-{side}')
    return totalpnl




def add_indicator(df):
    df['EMA_9']=df['close'].ewm(span=9,adjust=False).mean()
    
    df['EMA_21']=df['close'].ewm(span=21,adjust=False).mean()
    df['SMA_20']=df['close'].rolling(window=20).mean()
    df['SMA_50']=df['close'].rolling(window=50).mean()
    df['RSI_14']=ta.momentum.RSIIndicator(close=df['close'],window=14).rsi()
    df['ATR_14']=ta.volatility.AverageTrueRange(high=df['high'],low=df['low'],close=df['close'],window=14).average_true_range()
   
    return df


def generate_signals(df):
    print('generate signal')
    buy_signals=[]
    sell_signals=[]
    for i in range(1,len(df)):
        if df['RSI_14'].iloc[i-1]>=30 and df['RSI_14'].iloc[i]<=30:
            # pd.concat([buy_signals,df.iloc[i]])
            buy_signals.append(df.iloc[i])
        if df['RSI_14'].iloc[i-1]<=70 and df['RSI_14'].iloc[i]>=70:
            # pd.concat([buy_signals,df.iloc[i]])
            sell_signals.append(df.iloc[i])
    return pd.DataFrame(buy_signals),pd.DataFrame(sell_signals)

if __name__=='__main__':
    main()
