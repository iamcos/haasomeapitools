import gzip
import zlib
import base64
import timeit
from time import sleep
from functools import lru_cache
from botdatabase import BotDB
from botsellector import BotSellector
from haasomeapi.enums.EnumMadHatterIndicators import EnumMadHatterIndicators
from haasomeapi.enums.EnumMadHatterSafeties import EnumMadHatterSafeties
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
import time
from random import random
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
import pandas as pd
from numpy import arange
from ratelimit import limits, sleep_and_retry
from pathlib import Path
from datetime import datetime
import datetime
import jsonpickle
import interval as iiv
import csv
import pickle
import os
import json
from haasomeapi.enums.EnumCustomBotType import EnumCustomBotType


import configserver
from haasomeapi.HaasomeClient import HaasomeClient


class Haas():

	"""
	Haasonline trading software interaction class: get botlist, marketdata, create bots and configure their parameters, initiate backtests and so forth can be done through this class
	"""

	def __init__(self):
		self.c = self.client

	def client(self):
		ip, secret = configserver.validateserverdata()
		haasomeClient = HaasomeClient(ip, secret)
		return haasomeClient


class Bot(Haas):
	def __init__(self):
		Haas.__init__(self)


class MadHatterBot(Bot):

	def create_mh(self, input_bot, name):
		new_mad_hatter_bot = self.c().customBotApi.new_mad_hatter_bot_custom_bot(
			input_bot.accountId,
			input_bot.botType,
			name,
			input_bot.priceMarket.primaryCurrency,
			input_bot.priceMarket.secondaryCurrency,
			input_bot.priceMarket.contractName,
		)
		# print(new_mad_hatter_bot.errorCode, new_mad_hatter_bot.errorMessage)
		# print(new_mad_hatter_bot.result)
		return new_mad_hatter_bot.result

	@sleep_and_retry
	@limits(calls=3, period=2)
	def return_botlist(self):
		bl = self.c().customBotApi.get_all_custom_bots().result
		botlist = [x for x in bl if x.botType == 15]
		# print(botlist)
		return botlist

	def make_bot_from_bot_config(self, config, name):
		botname = (
			str(config.priceMarket.primaryCurrency)
			+ str(" / ")
			+ str(config.priceMarket.secondaryCurrency)
			+ str(" Roi ")
			+ str(config.roi))
		new_bot = self.create_mh(example_bot, botname)
		self.configure_mh_from_another_bot(config, new_bot)
		return new_bot.result

	def bruteforce_indicators(self, bot):

		d = self.bruteforce_rsi_corridor(bot)

	def bot_config(self, bot):
		botdict = {"pricesource": EnumPriceSource(bot.priceMarket.priceSource).name,
				   "primarycoin": bot.priceMarket.primaryCurrency,
				   "secondarycoin": bot.priceMarket.secondaryCurrency,
				   "interval": int(bot.interval),
				   "signalconsensus": bool(bot.useTwoSignals),
				   "resetmiddle": bool(bot.bBands["ResetMid"]),
				   "allowmidsells": bool(bot.bBands["AllowMidSell"]),
				   "matype": bot.bBands["MaType"],
				   "fcc": bool(bot.bBands["RequireFcc"]),
				   "rsil": str(bot.rsi["RsiLength"]),
				   "rsib": str(bot.rsi["RsiOversold"]),
				   "rsis": str(bot.rsi["RsiOverbought"]),
				   "bbl": str(bot.bBands["Length"]),
				   "devup": str(bot.bBands["Devup"]),
				   "devdn": str(bot.bBands["Devdn"]),
				   "macdfast": str(bot.macd["MacdFast"]),
				   "macdslow": str(bot.macd["MacdSlow"]),
				   "macdsign": str(bot.macd["MacdSign"]),
				   "roi": int(bot.roi),
				   "trades": int(len(bot.completedOrders)),
				   'orderbook': [{x: y for x, y in self.trades_to_df(bot).items()}]}

		return df

	def bruteforce_rsi_corridor(self, bot):
		rsi_l = int(bot.rsi['RsiLength'])
		applied = []
		bots = []
		print(rsi_l)
		d = [x for x in [rsi_l, rsi_l+1, rsi_l+2]]
		for x in d:
			print(x)
			botconfig = self.bot_config(bot)
			# print(botconfig)
			botconfig['rsil'] = x

			config, botobj = self.setup(bot, botconfig)
			applied.append(config)
		for x in range(rsi_l-3, bot.rsi['RsiLength'], -1):
			botconfig = self.bot_config(bot)
			botconfig['rsil'] = x

			config, botobj = self.setup(bot, botconfig)
			applied.append(config)

	def mad_hatter_base_parameters(self):
		ranges = {}
		ranges['interval'] = [1, 2, 3, 4, 5, 6, 10, 12, 15, 20,
							  30, 45, 60, 90, 120, 150, 180, 240, 300, 600, 1200, 2400]
		ranges["signalconsensus"] = [bool(True), bool(False)]
		ranges['resetmiddle'] = ranges['signalconsensus']
		ranges["allowmidsells"] = ranges['signalconsensus']
		ranges['matype'] = list([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
		ranges['fcc'] = ranges['signalconsensus']

		ranges['rsil'] = list(range(2, 21))
		ranges['rsib'] = list(range(2, 49))
		ranges['rsis'] = list(range(51, 99))
		ranges['bb'] = list(range(7, 60))
		ranges['devup'] = list(arange(0.1, 4.0))
		ranges['devdown'] = list(arange(0.1, 4.0))
		ranges['macdfast'] = list(range(2, 59, 2))
		ranges['macdslow'] = list(range(40, 80, 2))
		ranges['macdsign'] = list(range(3, 21, 2))
		df = pd.DataFrame(botdict, index=range(len(botdict)))
		return df

		configure = self.setup(bot, df)

	def trades_to_df(self, bot):
		if len(bot.completedOrders) > 0:
			completedOrders = [{'orderId': x.orderId, 'orderStatus': x.orderStatus, 'orderType': x.orderType, 'price': x.price, 'amount': x.amount,
								'amountFilled': x.amountFilled, 'date': pd.to_datetime(x.unixAddedTime, unit='s')} for x in bot.completedOrders]
			orders_df = pd.DataFrame(completedOrders)
			return orders_df

		else:
			# {'pair': None,
			completedOrders = [{'orderId': None, 'orderStatus': None, 'orderType': None, 'price': None,
								'amount': None, 'amountFilled': None, 'unixTimeStamp': datetime.today()}for x in range(1)]
			orders_df = pd.DataFrame(completedOrders)
		return orders_df
	# @sleep_and_retry
	# @limits(calls=3, period=2)

	def compare_indicators(self, bot, bot1):
		# print(bot.rsi, '\n',bot1.rsi)
		rsi = bot.rsi.items() == bot1.rsi.items()
		bbands = bot.bBands.items() == bot1.bBands.items()
		macd = bot.macd.items() == bot1.macd.items()
		interval = bot.interval == bot1.interval
		if rsi == True and bbands == True and macd == True and interval == True:
			return True
		else:
			# print('bot not alike')
			return False

	@sleep_and_retry
	@limits(calls=4, period=3)
	def identify_which_bot(self, ticks):
		results = []
		botlist = self.return_botlist()
		try:
			while True:

				botlist2 = self.return_botlist()
				lists = zip(botlist, botlist2)
				for x in lists:
					if x[0].guid == x[1].guid:
						# c = self.compare_indicators(lists[x][0], lists[x][1])
						c = self.compare_indicators(x[0], x[1])
						if c == False:
							botlist = botlist2
							# print(ticks)
							bot = self.bt_mh_on_update(x[1], ticks)
							results.append(bot)
						elif c == True:
							pass
						else:
							return results
		except KeyboardInterrupt:
			return results

	@sleep_and_retry
	@limits(calls=3, period=2)
	def bt_mh_on_update(self, bot, ticks):

		bt = self.c().customBotApi.backtest_custom_bot(
			bot.guid,
			int(ticks)
		)
		if bt.errorCode != EnumErrorCode.SUCCESS:
			print("bt", bt.errorCode, bt.errorMessage)
		else:
			# print(bt.result.roi)
			# print(bt.errorCode, bt.errorMessage)
			return bt.result

			# yeid


from functools import lru_cache
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from botsellector import BotSellector

from haasomeapi.enums.EnumIndicator import EnumIndicator
import pandas as pd
class TradeBot(Bot):

	def __init__(self):
		Bot.__init__(self)

	def return_bot(self, guid):
		bot = self.c().tradeBotApi.get_trade_bot(guid).result
		return bot
	def get_indicators(self,bot):
		'''
		returns all tradebot indicators as a list
		'''

		idd = list([bot.indicators[x] for x in bot.indicators])
		return idd

	def select_indicator(self,indicators):

		for i, b in enumerate(indicators):
			print(i, indicators[i].indicatorTypeFullName)
		uip = input('Select indicator')

		indicator = indicators[int(uip)]
		print('select indicator', indicator)
		return indicator
	def setup_indicator(self,bot,indicator):
		setup = self.c.TradeBotApi.setup_indicator(bot.guid, indicator.guid,
									   bot.priceMarket, bot.priceMarket.primaryCurrency, bot.priceMarket.secondaryCurrency, bot.priceMarket.contractName, indicator.timer, indicator.chartType, indicator.deviation)
		print(f'Indicator setup was a {setup.errorCode.value}, {setup.errorMessage.value}')
	def get_interfaces(self, bot, indicator):
		# print('indicator2', bot.indicators.__dict__)
		# returns select indicator interfaces
		# print(indicator.__dict__)
		interfaces = []
		for interface in bot.indicators[indicator.guid].indicatorInterface:
			interfaces.append({'title': interface.title, 'value': interface.value, 'options': interface.options, 'step': interface.step})

		return interfaces



	# def get_full_interfaces(self, bot, indicator):
	# 	interfaces ={}
	# 	for interface in bot.indicators[indicator.guid].indicatorInterface:
	# 		interfaces[EnumIndicator(bot.indicators[indicator.guid].indicatorType).name] = interface

	# 	print(interfaces)

	# 	return interfaces


	def dict_from_class(self,cls):

		 return dict(
					 (key, value)
					 for (key, value) in cls.__dict__.items()

				 )
	def get_full_interfaces(self, bot, indicator):
		interfaces = {}
		for interface in bot.indicators[indicator.guid].indicatorInterface:
			interfaces[EnumIndicator(
				bot.indicators[indicator.guid].indicatorType).name] = self.dict_from_class(interface)

		# print(interfaces)


		return interfaces
	def get_enums_for_indicators(self, bot):
		icc = ic()
		indicators_enums = {}
		for indicator in bot.indicators:
			indicator_enum = icc().get_indicator_enum_data(
				bot.indicators[indicator].indicatorInterface.indicatorType)
			indicators.append(indicator_enum)
		return indicators_enums


		return indicators
	def add_indicator(self, bot, indicator):
		failed = []
		try:
			add = self.c().tradeBotApi.add_indicator(bot.guid, indicator)
			if add.result:
				print('Indicator', EnumIndicator(indicator).name, ' added to ', bot.name)
			else:
				print('Adding indicator didn\'t work out')

		except:
			failed.append(indicator)
		return failed


	def edit_indicator(self, bot, indicator, field, value):
		print(indicator)
		indicator_config = self.c().tradeBotApi.edit_bot_indicator_settings(
			bot.guid, indicator.guid, field, value)
		# print('field',field,'value',value)
		# print(indicator_config.errorMessage, indicator_config.errorCode)
		# print('edit_indicators get indicator interface', indicator)
		interfaces = self.get_interfaces(bot, indicator)
		# for interface in interfaces:
		# 	print(interface)
		# print(indicator_config.result.__dict__)
		# print(indicator_config.result.name)
		# print(indicator_config.result.Indicators[indicator.guid])
		return indicator_config

	def remove_indicator(self, bot, indicator):
		failed = []
		try:
			add = self.c().tradeBotApi.remove_indicator(bot.guid, indicator.guid)
			if add.result:
				print('Indicator', EnumIndicator(indicator).value, ' removed from ', bot.name)
			else:
				print('Removing indicator didn\'t work out')

		except:
			failed.append(indicator)
		return failed

	def remove_indicators(self, bot, indicator_list):
		for x in indicator_list:
			self.remove_indicator(bot, x)


	def add_multiple_indicators(self, bot, indicators):
		for x in indicators:
			self.add_indicator(bot, x)

	def add_all_indicators(self,bot):
		indicators = [x for x in range(71)]
		self.add_multiple_indicators(bot,indicators)

	def remove_all_indicators(self,bot):
		indicators = t.get_indicators(bot)
		self.remove_indicators(bot, indicators)

	def select_bot_get_indicator(self,bot):
		indicators = self.get_indicators(bot)
		indicator = self.select_indicator(indicators)
		return indicator



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



def main():
	all_markets = MarketData().get_all_markets()
	# print(all_markets.pricesource.unique())
	# print(len(all_markets.pricesource.unique()))
	# print(all_markets.primarycurrency.unique())
	# print(len(all_markets.primarycurrency.unique()))
	all_markets[['pricesource', 'primarycurrency', 'secondarycurrency']].to_csv('all_markets_pairs.csv')
	all_markets[['primarycurrency', 'secondarycurrency']].to_csv('all_pairs.csv')
	all_markets.pricesource.to_csv('all_exchanges.csv')
	print(EnumPriceSource(all_markets.obj[0].priceSource))
	# all_markets.to_csv('all_markets.csv')
	print(all_markets.obj[0].priceSource)
if __name__ == "__main__":
	main()
