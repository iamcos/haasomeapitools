from BaseHaas import Haas
import requests
import json
import pandas as pd
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
from time import sleep
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
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

				"date": x.unixTimeStamp,
				"open": x.open,
				"high": x.highValue,
				"low": x.lowValue,
				"close": x.close,
				"buy": x.currentBuyValue,
				"sell": x.currentSellValue,
				"volume": x.volume,
			}
			for x in market_history
		]

		df = pd.DataFrame(market_data)
		df['date'] = pd.to_datetime(df['date'], unit = 's')
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
                            "secondarycurrency", "obj"]),
		)
		return df

	def return_priceMarket_object(self,  pricesource, primarycoin, secondarycoin):
		# print(pricesource, primarycoin, secondarycoin)
		df = self.get_all_markets()
		'''
			Returns priceSource object for given pricesorce, primarycoin, secondarycoin if that pricesource is enabled in Haas.
		'''

		obj = df[df["pricesource"] == pricesource][df["primarycurrency"]
                                             == primarycoin][df["secondarycurrency"] == secondarycoin].values
		print('obj',obj)
		print('obj1', obj[0][3])
		return obj[0][3]

	def db_table(self):

		db_tables = {}
		market_data_cols = ['dt', 'open', 'close', 'volume', 'buy', 'sell']
		indicator_cols = ['dt', 'val1','val2','val3']

	def get_market_data(self, priceMarketObject, interval, depth):
			marketdata = self.c().marketDataApi.get_history_from_market(
				priceMarketObject, interval, int(depth))
			print(marketdata.errorCode, marketdata.errorMessage)
			while marketdata.errorCode != EnumErrorCode.SUCCESS:
				# if marketdata.errorCode != EnumErrorCode.SUCCESS:
							marketdata = self.c().marketDataApi.get_history_from_market(
														priceMarketObject, interval, depth)
							print(marketdata.errorCode, marketdata.errorMessage)
			else:
				print('len of market data ', len(marketdata.result))
				df = self.to_df_for_ta(marketdata.result)
				print(df)

				return df

			"""
			Below are DASH recepies for market related data
			"""


	def markets_dropdown(self):

		markets = self.get_all_markets()
		markets_dropdown = [{'label': str(x), 'value': str(
			x)} for x in markets.pricesource.unique()]
		return markets_dropdown


	def primarycoin_dropdown(self8, pricesource,):

		df = self.get_all_markets()
		pairs = df[df["pricesource"] == pricesource]
		primary_coin_dropdown = [{'label': str(x), 'value': str(
			x)} for x in pairs.primarycurrency.unique()]

		return primary_coin_dropdown


	def secondary_coin_dropdown(self, primarycoin, pricesource,):

		df = self.get_all_markets()
		pairs = df[df["pricesource"] ==
				pricesource][df['primarycurrency'] == primarycoin]
		# print(pairs)
		secondary_coin_dropdown = [{'label': str(x), 'value': str(
			x)} for x in pairs.secondarycurrency.unique()]
		# print(secondary_coin_dropdown)
		return secondary_coin_dropdown

	def get_last_minute_ticker(self, marketobj):
		ticker = self.c().marketDataApi.get_minute_price_ticker_from_market(marketobj)
		df = self.to_df_for_ta(ticker.result)
		return df


print(MarketData().empty_market_data_df().head())
