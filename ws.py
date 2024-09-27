import websockets
import json
import pandas as pd
import logging
# WebSocket 处理函数，接收实时数据并输出
async def binance_kline(df,bot,chatid):
    s=df
    uri = "wss://stream.binance.com:9443/ws/btcusdt@kline_15m"  # Binance 1分钟K线
    
    async with websockets.connect(uri) as websocket:
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
                buy,sell=generate_signals(s)  
                buysignal=buy.iloc[-1]
                sellsignal=sell.iloc[-1]
                if buysignal['timestamp']==timestamp:
                    logging.info('{timestamp} buy signal {close_price}')
                    message=f'{timestamp} buy signal {close_price}'
                    bot.send_message(chat_id=chatid, text=message)
                if sellsignal['timestamp']==timestamp:
                    logging.info('{timestamp} sell signal {close_price}')
                    message=f'{timestamp} sell signal {close_price}'
                    bot.send_message(chat_id=chatid, text=message)



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
