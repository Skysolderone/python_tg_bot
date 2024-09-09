import asyncio
import websockets
import json
import pandas as pd

# WebSocket 处理函数，接收实时数据并输出
async def binance_kline():
    uri = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"  # Binance 1分钟K线
    async with websockets.connect(uri) as websocket:
        while True:
            # 接收WebSocket数据
            message = await websocket.recv()
            data = json.loads(message)
            
            # 解析K线数据
            kline = data['k']
            is_kline_closed = kline['x']  # K线是否结束
            timestamp = pd.to_datetime(kline['t'], unit='ms')
            open_price = float(kline['o'])
            high_price = float(kline['h'])
            low_price = float(kline['l'])
            close_price = float(kline['c'])

            # 输出K线数据
            print(f"时间: {timestamp}")
            print(f"开盘价: {open_price}, 最高价: {high_price}, 最低价: {low_price}, 收盘价: {close_price}")
            print(f"K线结束: {is_kline_closed}")
            print("="*40)

# 运行 WebSocket 数据接收
asyncio.run(binance_kline())

