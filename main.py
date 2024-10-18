from  binance.client import Client
from binance.exceptions import BinanceAPIException
import dotenv
import os
from datetime import datetime,timedelta
import time
import pandas as pd
import ta.momentum
import ta.volatility
# from get_csv.csvdata import Csv
import ta
import asyncio
# from ws import binance_kline
import logging
from telegram import Bot
import redis
import json
import websockets
# 配置日志
logging.basicConfig(
    filename='app.log',  # 指定日志文件名
    filemode='a',        # 'a' 表示追加模式（如果文件存在就追加日志）
    format='%(asctime)s - %(levelname)s - %(message)s',  # 日志格式
    level=logging.INFO   # 日志级别为 INFO
)
position=1
price=0.00
addPosition=1
side=''
totalBalance=0.00
totalpnl=0
r=redis.Redis('localhost',port=6379,db=0)
def getKline(client):
        today=datetime.now()
        today_str=today.strftime('%Y-%m-%d')
        # symbol = 'BTCUSDT'  # 设置交易对
        symbol = 'ETHUSDT'  # 设置交易对
        intervals = ['15m', '30m', '1h', '2h', '4h','1d']  # 定义时间周期
        # intervals = ['1d']  # 定义时间周期
        # start_date = '2017-08-01'  区间太长，狗在创世期间买入现在都是亿万富翁
        start_date='2024-08-01'
        end_date = today_str
        for interval in intervals:
            indexpd=f"csv/{interval}.csv"
            intervavpd=pd.DataFrame()
            if os.path.exists(indexpd):
                    intervavpd=pd.read_csv(indexpd)
                    final=intervavpd.iloc[-1]
                    if not final.empty:
                        s=final.to_dict()['timestamp']
                        start_date=s.replace(' 00:00:00','')
                    if start_date==end_date:
                        continue 
            print(f"Fetching {interval} data...")
            klines = get_klines(client,symbol, interval, start_date, end_date)
            filename = f"csv/{interval}.csv"
            save_to_csv(intervavpd,klines, filename)
            print(f"Data saved to {filename}")
def get_klines(client,symbol, interval, start_str, end_str):
        """
        获取K线数据

        :param symbol: 交易对，例如 'BTCUSDT'
        :param interval: K线周期，例如 '15m', '30m', '1h', '2h', '4h', '1d'
        :param start_str: 开始时间，例如 '2017-08-01'
        :param end_str: 结束时间，例如 '2024-09-12'
        :return: K线数据
        """
        klines = []
        # print(start_str)
        start_date = datetime.strptime(start_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_str, '%Y-%m-%d')
        while start_date < end_date:
            end_date_batch = start_date + timedelta(days=30)  # 可以调整为更小的时间范围，确保每次请求不超过15000条数据
            if end_date_batch > end_date:
                end_date_batch = end_date
            klines_batch = client.get_historical_klines(symbol, interval, start_date.strftime('%Y-%m-%d'), end_date_batch.strftime('%Y-%m-%d'))
            if not klines_batch:
                break
            klines.extend(klines_batch)
            start_date = end_date_batch
        return klines
def save_to_csv(olddata,data, filename):
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 
            'close_time', 'quote_asset_volume', 'number_of_trades', 
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 
            'ignore'
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['open']=df['close'].astype(float)
        df['high']=df['high'].astype(float)
        df['low']=df['low'].astype(float)
        df['close']=df['close'].astype(float)

        result=pd.concat([olddata,df])
        # unique=result.drop_duplicates(subset='timestamp')
        # unique=unique.sort_values(by=['timestamp']).reset_index(drop=True)
        result.to_csv(filename, index=False)
async def main():
    dotenv.load_dotenv()
    #binance client init 
    print('client init')
    apikey=os.getenv('apikey')
    secret=os.getenv('secret')
    client=Client(apikey,secret)

    #anthor get binance kline data save to csv 00:00
    getKline(client)
    token=os.getenv('bot_api')
    chatId=os.getenv('tgchatid')
    bot=Bot(token=token)
    
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
    #pd15m=pd.read_csv('csv/15m.csv')
    # pd30m=pd.read_csv('csv/30m.csv')
    # pd1h=pd.read_csv('csv/1h.csv')
    # pd2h=pd.read_csv('csv/2h.csv')
    pd4h=pd.read_csv('csv/4h.csv')
    pd1d=pd.read_csv('csv/1d.csv')

   
    
   
    #concat kline data
    #unique15m=pd15m.drop_duplicates(subset='timestamp')
    #unique15m=unique15m.sort_values(by=['timestamp']).reset_index(drop=True)
    # unique30m=pd30m.drop_duplicates(subset='timestamp')
    # unique30m=unique30m.sort_values(by=['timestamp']).reset_index(drop=True)
    # unique1h=pd1h.drop_duplicates(subset='timestamp')
    # unique1h=unique1h.sort_values(by=['timestamp']).reset_index(drop=True)
    # unique2h=pd2h.drop_duplicates(subset='timestamp')
    # unique2h=unique2h.sort_values(by=['timestamp']).reset_index(drop=True)
    unique4h=pd4h.drop_duplicates(subset='timestamp')
    unique4h=unique4h.sort_values(by=['timestamp']).reset_index(drop=True)
    unique1d=pd1d.drop_duplicates(subset='timestamp')
    unique1d=unique1d.sort_values(by=['timestamp']).reset_index(drop=True)
    arr={}

    #load indicator
    print('load indicator')
    #df15m=add_indicator(unique15m)
    #arr['15m']=df15m
    # df30m=add_indicator(unique30m)
    # arr['30m']=df30m
    # df1h=add_indicator(unique1h)
    # arr['1h']=df1h
    # df2h=add_indicator(unique2h)
    # arr['2h']=df2h
    # df4h=add_indicator(unique4h)
    # arr['4h']=df4h
    # df1d=add_indicator(unique1d)
    # arr['1d']=df1d
      
    # for i,v in arr.items():
    #     #check indicator  buy|sell
    #     buy,sell=generate_signals(v)  
    #     buy['signal']='buy'
    #     sell['signal']='sell'
    #     change=pd.DataFrame()
    #     change=pd.concat([buy,sell])
    #     change=change.sort_values(by=['timestamp']).reset_index(drop=True)
    #     #check pnl
    #     pnl=runCheckPnl(change)
    #     print(f'{i}:{pnl}')
    # 运行 WebSocket 数据接收
    await bot.send_message(chat_id=chatId,text=f'init bot success')
    # await binance_kline(df15m,bot,chatId)
    url="wss://stream.binance.com:9443/ws/btcusdt@kline_4h"
    htime=r.get('4h')
    if htime is None:
        htime=time.time()
    if htime<=0:
        htime=time.time()
    label=1
    await binance_klineV2(label,url,unique4h,bot,chatId,htime)
    url="wss://stream.binance.com:9443/ws/btcusdt@kline_1d"
    dtime=r.get('1d')
    if dtime is None:
        dtime=time.time()
    if dtime<=0:
        dtime=time.time()
    label=2
    await binance_klineV2(label,url,unique1d,bot,chatId,dtime)
    

def runCheckPnl(change):
    totalpnl=0.00
    position=0.1
    addPosition=0.02
    side=''
    for index,v in change.iterrows():
        if v['signal']=='buy':
            if side=='':
                # position=0.01
                side='long'
                totalBalance=position*v['close']
                price=v['close']
                pnl=0
                time=v['timestamp']
                print(f'多单买入:{time}-{price}-{position}-{totalBalance}-{side}')
                continue
            if side=='long':
                position=position+addPosition
                totalBalance=totalBalance+v['close']*addPosition
                price=totalBalance/position
                pnl=0
                time=v['timestamp']     
                print(f'多单补仓:{time}-持仓均价{price}-{position}-{totalBalance}-{side}')
                continue

            if side=='short':
                price=v['close']
                sellbalance=price*position  
                pnl=totalBalance-sellbalance
                side=''
                totalpnl=totalpnl+pnl
                # if pnl<0:
                #     totalpnl=totalpnl-pnl
                # else :
                #     totalpnl=totalpnl+pnl
                time=v['timestamp']
                print(f'空单平仓:{time}|{price}|{position}-{totalBalance}|{pnl}')
                # position=0.01
                position=0.1
                side='long'
                totalBalance=position*v['close']
                price=v['close']
                pnl=0
                print(f'多单买入:{time}-{price}-{position}-{totalBalance}-{side}')
                continue
        if v['signal']=='sell':
            if side=='':
                # position=0.01
                side='short'
                totalBalance=position*v['close']
                price=v['close']
                pnl=0
                time=v['timestamp']
                print(f'空单开仓:{time}-{price}-{position}-{totalBalance}-{side}')
                continue
            if side=='long':
                price=v['close']
                sellbalance=price*position
                pnl=sellbalance-totalBalance
                side=''
                totalpnl=totalpnl+pnl
                time=v['timestamp']
                print(f'多单平仓:{time}|{price}|{position}|{totalBalance}|{pnl}')
                side='short'
                position=0.1
                totalBalance=position*v['close']
                price=v['close']
                pnl=0
                print(f'空单开仓:{time}-{price}-{position}-{totalBalance}-{side}')
                continue
            if side=='short':
                position=position+addPosition
                
                totalBalance=totalBalance+v['close']*addPosition
                
                price=totalBalance/position
                pnl=0
                time=v['timestamp']
                print(f'空单补仓:{time}-持仓均价{price}-{position}-{totalBalance}-{side}')
                continue
    return totalpnl




def add_indicator(df):
    df['EMA_12']=df['close'].ewm(span=12,adjust=False).mean()
    df['EMA_26']=df['close'].ewm(span=26,adjust=False).mean()
    df['SMA_20']=df['close'].rolling(window=20).mean()
    df['SMA_50']=df['close'].rolling(window=50).mean()
    df['RSI_14']=ta.momentum.RSIIndicator(close=df['close'],window=14).rsi()
    df['ATR_14']=ta.volatility.AverageTrueRange(high=df['high'],low=df['low'],close=df['close'],window=14).average_true_range()
    df['EMA-Buy']=(df['EMA_12']>df['EMA_26']).astype(int)
    df['EMA-Sell']=(df['EMA_12']<df['EMA_26']).astype(int)
    df['SMA-Buy']=(df['SMA_20']>df['SMA_50']).astype(int)
    df['SMA-Sell']=(df['SMA_20']<df['SMA_50']).astype(int)
    
    return df


async def binance_klineV2(label,url,df,bot,chatid,sendtime):
    s=df
    async with websockets.connect(url) as websocket:
        while True:
            # 接收WebSocket数据
            message = await websocket.recv()
            data = json.loads(message)
            
            # 解析K线数据
            kline = data['k']
            is_kline_closed = kline['x']  # K线是否结束
            timestamp = pd.to_datetime(kline['t'], unit='ms')
            endtimestamp = pd.to_datetime(kline['T'], unit='ms')
            open_price = float(kline['o'])
            high_price = float(kline['h'])
            low_price = float(kline['l'])
            close_price = float(kline['c'])

            # 输出K线数据
            # print(f"时间: {timestamp}")
            # print(f"开盘价: {open_price}, 最高价: {high_price}, 最低价: {low_price}, 收盘价: {close_price}")
            # print(f"K线结束: {is_kline_closed}")
            # print("="*40)
            if is_kline_closed:
                data = {
    'timestamp': [timestamp],  # 示例时间戳（毫秒）
    'open': [open_price],
    'high': [high_price],
    'low': [low_price],
    'close': [close_price],
    'volume': [1.5],
    'close_time': [endtimestamp],  # 示例关闭时间戳（毫秒）
    'quote_asset_volume': [60000.0],
    'number_of_trades': [10],
    'taker_buy_base_asset_volume': [0.5],
    'taker_buy_quote_asset_volume': [20000.0],
    'ignore': [0]  # 这里可以根据需要设置
}
                s=pd.concat([s,data])
                # buy,sell=generate_signals(s)  
                # buysignal=buy.iloc[-1]
                # sellsignal=sell.iloc[-1]
                # if buysignal['timestamp']==timestamp:
                #     logging.info('{timestamp} buy signal {close_price}')
                #     message=f'{timestamp} buy signal {close_price}'
                #     bot.send_message(chat_id=chatid, text=message)
                # if sellsignal['timestamp']==timestamp:
                #     logging.info('{timestamp} sell signal {close_price}')
                #     message=f'{timestamp} sell signal {close_price}'
                #     bot.send_message(chat_id=chatid, text=message)
                _,buy,sell=calculate_td_sequential_with_signals(s)
                buysignal=buy.iloc[-1]
                sellsignal=sell.iloc[-1]
                if buysignal['timestamp']>sendtime:
                    logging.info('{timestamp} buy signal {close_price}')
                    message=f'{timestamp} buy signal {close_price}'
                    t=time.time()
                    if label==1:
                        r.set('4h',t)
                    elif label==2:
                        r.set('1d',t)
                    bot.send_message(chat_id=chatid, text=message)
                if sellsignal['timestamp']>sendtime:
                    logging.info('{timestamp} sell signal {close_price}')
                    message=f'{timestamp} sell signal {close_price}'
                    t=time.time()
                    if label==1:
                        r.set('4h',t)
                    elif label==2:
                        r.set('1d',t)
                    bot.send_message(chat_id=chatid, text=message)





def calculate_td_sequential_with_signals(data):
    """
    计算给定价格序列的 TD Sequential 并标记买入和卖出信号，同时分别存储这些信号。
    
    参数:
    data (pd.DataFrame): 包含 'close' 列的 DataFrame，代表收盘价
    
    返回:
    pd.DataFrame: 返回包含 TD 指标和买入/卖出信号的 DataFrame
    List: 返回买入信号和卖出信号的列表
    """
    data['TD_Seq'] = 0  # 初始化计数列
    data['Buy_Signal'] = None  # 初始化买入信号列
    data['Sell_Signal'] = None  # 初始化卖出信号列

    # 分别存储买入和卖出信号的列表
    buy_signals = []
    sell_signals = []

    # 遍历数据
    for i in range(4, len(data)):
        # 买入 Setup 条件
        if data['close'].iloc[i] < data['close'].iloc[i - 4]:
            data.at[i, 'TD_Seq'] = data['TD_Seq'].iloc[i - 1] + 1 if data['TD_Seq'].iloc[i - 1] > 0 else 1
        # 卖出 Setup 条件
        elif data['close'].iloc[i] > data['close'].iloc[i - 4]:
            data.at[i, 'TD_Seq'] = data['TD_Seq'].iloc[i - 1] - 1 if data['TD_Seq'].iloc[i - 1] < 0 else -1
        else:
            data.at[i, 'TD_Seq'] = 0  # 不满足条件时重置计数

        # 如果计数达到 9，标记买入或卖出信号，并重置计数
        if data['TD_Seq'].iloc[i] == 9:
            data.at[i, 'Buy_Signal'] = data['close'].iloc[i]
            buy_signals.append({'index': i, 'price': data['close'].iloc[i]})  # 记录买入信号
            data.at[i, 'TD_Seq'] = 0  # 重置计数
        elif data['TD_Seq'].iloc[i] == -9:
            data.at[i, 'Sell_Signal'] = data['close'].iloc[i]
            sell_signals.append({'index': i, 'price': data['close'].iloc[i]})  # 记录卖出信号
            data.at[i, 'TD_Seq'] = 0  # 重置计数

    return data, buy_signals, sell_signals
def generate_signals(df):
    buy_signals=[]
    sell_signals=[]
    for i in range(1,len(df)):
        if  df['RSI_14'].iloc[i-1]>=30 and df['RSI_14'].iloc[i]<=30:
            # pd.concat([buy_signals,df.iloc[i]])
            buy_signals.append(df.iloc[i])
        if df['RSI_14'].iloc[i-1]<=70 and df['RSI_14'].iloc[i]>=70:
            # pd.concat([buy_signals,df.iloc[i]])
            sell_signals.append(df.iloc[i])
    return pd.DataFrame(buy_signals),pd.DataFrame(sell_signals)


if __name__=='__main__':
    asyncio.run(main())
