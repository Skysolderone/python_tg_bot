from datetime import datetime,timedelta
import pandas as pd
import os
class Csv:
    def __init__(self) -> None:
        pass
    def getKline(self,client):
        today=datetime.now()
        today_str=today.strftime('%Y-%m-%d')
        # symbol = 'BTCUSDT'  # 设置交易对
        symbol = 'ETHUSDT'  # 设置交易对
        intervals = ['15m', '30m', '1h', '2h', '4h']  # 定义时间周期
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
            klines = self.get_klines(client,symbol, interval, start_date, end_date)
            filename = f"csv/{interval}.csv"
            self.save_to_csv(intervavpd,klines, filename)
            print(f"Data saved to {filename}")
    def get_klines(self,client,symbol, interval, start_str, end_str):
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
    def save_to_csv(self,olddata,data, filename):
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