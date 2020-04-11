from BaseHaas import Haas
import requests
import json
import pandas as pd
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
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
			return df

	def to_df_for_ta(self, market_history):

		market_data = [
			{

				"date": x.timeStamp,
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
		df['D'] = pd.to_datetime(df['D'])
		df.set_index(pd.DatetimeIndex(df['D']))
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
		print(obj)
		print(obj[0][3])
		return obj[0][3]

	def db_table(self):

		db_tables = {}
		market_data_cols = ['dt', 'open', 'close', 'volume', 'buy', 'sell']
		indicator_cols = ['dt', 'val1','val2','val3']

	def get_market_data(self, priceMarketObject, interval, depth):

			count = 0
			marketdata = self.c().marketDataApi.get_history_from_market(
				priceMarketObject, interval, depth)
			if marketdata.errorCode != 'SUCCESS':
				for r in range(2):
					print(marketdata.errorCode.value, marketdata.errorMessage)
					marketdata = self.c().marketDataApi.get_history_from_market(
										priceMarketObject, interval, depth)
			else:
				df = self.to_df_for_ta(marketdata.result)
				print(df)

				return df
