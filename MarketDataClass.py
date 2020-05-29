from BaseHaas import Haas
import requests
import json
import pandas as pd
import csv
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
from time import sleep
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from ratelimit import limits, sleep_and_retry
class MarketData(Haas):
    def __init__(self):
        Haas.__init__(self)
        # self.bt_db = sqllite_memory = sqllite.client("market.db")

    def get_ticks(self,pricesource, primarycoin, secondarycoin,interval,tickstype):

        '''
        Get price history in required tick intervals from Haaas online market data interface.
        tickstype can be LASTTICKS or DEEPTICKS
        result = dataframe with date_time index, Open(O), Close(C) High(H), Low(L),Buy(B), Sell(S), Volume(V), Unixtime(T) tables
        '''

        url = f'https://hcdn.haasonline.com/PriceAPI.php?channel={tickstype}&market={pricesource}_{primarycoin}_{secondarycoin}_&interval={interval}'

        with requests.sessions.Session() as s:
            resp = s.get(url)
            data_dict = resp.json().get('Data')
            # print(data_dict)
            index = []
            for d in data_dict:
                    index.append(pd.to_datetime(d['T'], unit='s'))

            df = pd.DataFrame(data_dict, index=index)
            df = df.rename(columns={'O':'open','C':'close','L':'low','H':'high','V':'volume'})
            # print(df)
            print(df)
            return df

    def empty_market_data_df(self):
        market_history = {'date': '', 'open':'','high':'','low':'', 'close':'','buy':'', 'sell':'', 'volume':''}
        df = pd.DataFrame(market_history,index=([""]))
        return df

    def to_df_for_ta(self, market_history):

        market_data = [
            {

                "Date": x.unixTimeStamp,
                "Open": x.open,
                "High": x.highValue,
                "Low": x.lowValue,
                "Close": x.close,
                "Buy": x.currentBuyValue,
                "Sell": x.currentSellValue,
                "Volume": x.volume,
            }
            for x in market_history
        ]
        print(market_data)
        df = pd.DataFrame(market_data)

        try:
            df['Date'] = pd.to_datetime(df['Date'], unit = 's')

        except:
            print('Whops')
  # print(df.index)
        return df
    def get_all_markets(self):

        markets = [
            (
                EnumPriceSource(i.priceSource).name,
                i.primaryCurrency,
                i.secondaryCurrency,
                i,
            )
            for i in self.c().marketDataApi.get_all_price_markets().result
        ]

        df = pd.DataFrame(
            markets,
            columns=(["pricesource", "primarycurrency",
                            "secondarycurrency", "obj"]
        ))
        return df

    def return_priceMarket_object(self,  pricesource, primarycoin, secondarycoin):
        # print(pricesource, primarycoin, secondarycoin)
        df = self.get_all_markets()
        '''
            Returns priceSource object for given pricesorce, primarycoin, secondarycoin if that pricesource is enabled in Haas.
        '''

        obj = df[df["pricesource"] == pricesource][df["primarycurrency"]
                                             == primarycoin][df["secondarycurrency"] == secondarycoin]
        # print('Market obj',obj.obj[0]__dict__)
        # print('obj1', obj[0][3])
        return obj.obj.values[0]
    def db_table(self):

        db_tables = {}
        market_data_cols = ['dt', 'open', 'close', 'volume', 'buy', 'sell']
        indicator_cols = ['dt', 'val1','val2','val3']

    @sleep_and_retry
    @limits(calls=1, period=3)
    def get_market_data(self, priceMarketObject, interval, depth):
            marketdata = self.c().marketDataApi.get_history_from_market(
            priceMarketObject, interval, depth)
            print(marketdata.errorCode, marketdata.errorMessage)
            df = self.to_df_for_ta(marketdata.result)
            return df

    def save_market_data_to_csv(self, marketData, marketobj):
        filename = f'{EnumPriceSource(marketobj.priceSource).name}|{marketobj.primaryCurrency}|{marketobj.secondaryCurrency}.csv'

        marketData.to_csv(f'./market_data/{filename}')
        print(f'{EnumPriceSource(marketobj.priceSource).name} | {marketobj.primaryCurrency} | {marketobj.secondaryCurrency} sucessfuly saved to csv')
        return f"sucessfully saved {filename} to market_data folder, with {len(marketData)} ticks included"

    def read_csv(self,file,nrows=None):
        data = pd.read_csv(file,nrows=nrows)
        def uppercase(x): return str(x).capitalize()
        data.rename(uppercase, axis='columns', inplace=True)
        data['Data'] = pd.to_datetime(data['Data'])
        dti = pd.DatetimeIndex([x for x in data['Date']])
        data.set_index(dti, inplace=True)
        print(data)
        # data['Date'] = pd.to_datetime(data['timestamp'])
        return data


    def stream_orderbook(self, pricemarketObject):
        request = self.c().marketDataApi.get_order_book_from_market(pricemarketObject)
        orderbook = request.result
        return orderbook

    def all_markets_orderbook(self, pricemarketobjlist):
        for i in pricemarketobjlist['obj']:

            orderbook = self.stream_orderbook(i)
            pricemarketobjlist['orderbook'] = orderbook
            # print(orderbook.__dict__)

        return pricemarketobjlist
    def calculate_expected_roi(self, market_data):
        diff = market_data.max()-market_data.min()
        expected = diff/market_data.max()*100
        print(f'expected roi: {expected}')
    def all_markets_to_object(self):
        pricemarketobjlist = []
        for i in self.get_all_markets().index:
            mard = self.get_all_markets().loc[i]
            priceobj = self.return_priceMarket_object(mard.pricesource, mard.primarycurrency, mard.secondarycurrency)
            pricemarketobjlist.append(priceobj)
        return pricemarketobjlist

        """
        Below are DASH recepies for market related data
        """
    def markets_dropdown(self):

        markets = self.get_all_markets()
        markets_dropdown = [{'label': str(x), 'value': str(
            x)} for x in markets.pricesource.unique()]
        return markets_dropdown


    def primarycoin_dropdown(self, pricesource,):

        df = self.get_all_markets()
        pairs = df[df["pricesource"] == pricesource]

        return pairs.primarycurrency.unique()

    def secondary_coin_dropdown(self, pricesource, primarycurrency):

        df = self.get_all_markets()
        df = self.get_all_markets()
        pairs = df[df["pricesource"] == pricesource][df['primarycurrency'] == primarycurrency]
        return pairs.secondarycurrency.unique()

    def get_last_minute_ticker(self, marketobj):
        ticker = self.c().marketDataApi.get_minute_price_ticker_from_market(marketobj)
        df = self.to_df_for_ta(ticker.result)
        return df
