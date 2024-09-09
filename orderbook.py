import asyncio
import websockets
import json

# WebSocket 处理函数，接收订单簿深度数据并输出
async def binance_order_book():
    uri = "wss://stream.binance.com:9443/ws/btcusdt@depth50"  # Binance BTC/USDT 20档订单簿深度
    async with websockets.connect(uri) as websocket:
        while True:
            # 接收WebSocket数据
            message = await websocket.recv()
            data = json.loads(message)
            
            # 提取订单簿数据
            last_update_id = data['u']  # 更新ID
            bids = data['b']  # 买单深度
            asks = data['a']  # 卖单深度

            # 打印更新的订单簿
            print(f"订单簿更新ID: {last_update_id}")
            print("买单 (价格, 数量):")
            for bid in bids:
                print(f"价格: {bid[0]}, 数量: {bid[1]}")
            
            print("卖单 (价格, 数量):")
            for ask in asks:
                print(f"价格: {ask[0]}, 数量: {ask[1]}")
            
            print("="*40)

# 运行 WebSocket 数据接收
asyncio.run(binance_order_book())
