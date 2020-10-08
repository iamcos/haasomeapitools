
import pandas as pd
from BaseHaas import MarketData
from functools import lru_cache
from BaseHaas import Main_Menu
from elasticsearch import Elasticsearch
@lru_cache()
def return_all_pairs():
        markets = MarketData().get_all_markets()
        # print(len(markets.Ticker.unique()))
        # print(markets)
        market = MarketData().return_priceMarket_object(21,ticker='ZILUSDT')
        print(market.__dict__)
        return markets

def convert_ticker(check=['BTCUSDT']):
        list = return_all_pairs()
        
def test():
        m = Main_Menu().return_marketobjects_from_tradingview_csv_file()
if __name__ == "__main__":
        # return_all_pairs()
#     return_coin_pair()
        # test()
        pass

es = Elasticsearch('127.0.0.1:9200').data_frame
print(es)
