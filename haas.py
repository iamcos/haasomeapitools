import configserver
from haasomeapi.HaasomeClient import HaasomeClient
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from sqlalchemy import create_engine
import sqlite3 as sqllite
from datetime import datetime
import requests
import json
from time import sleep
import pandas as pd
import numpy as np
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
from botsellector import BotSellector
from scipy import optimize
import interval as iiv
import functools


class Haas():
	"""
	Haasonline trading software interaction class: get botlist, marketdata, create bots and configure their parameters, initiate backtests and so forth can be done through this class
	"""
	def __init__(self):
		self.c = self.client
	def client(self):
		ip, secret = configserver.validateserverdata()
		haasomeClient = HaasomeClient(ip, secret)
		return haasomeClient()

class Bot(Haas):
	def __init__(self):
		Haas.__init__(self)


class TradeBot(Bot):

	def __init__(self):
		Bot.__init__(self)

	def get_indicators(self,bot):
		#returns all tradebot indicators
		indicators = {}
		idd = list([bot.indicators[x] for x in bot.indicators])

		for indicator in bot.indicators:
			indicators[bot.indicators[indicator].indicatorTypeShortName] = indicator
		# print(idd)
		# df = pd.DataFrame(indicators)
		# print(df)
		return idd

	def select_indicator(self,indicators):

		# print(indicators[0].indicatorTypeFullName)
		for i, b in enumerate(indicators):
			print(i, indicators[i].indicatorTypeFullName)
		uip = input('Select indicator')

		indicator = indicators[int(uip)]
		# print(indicator)
		return indicator
	def setup_indicator(self, indicator):
		self.c.TradeBotApi.setup_indicator(bot.guid, indicator.guid,
                                       bot.priceMarket, bot.priceMarket.primaryCurrency, bot.priceMarket.secondaryCurrency, bot.priceMarket.contractName, indicator.timer, indicator.chartType, indicator.deviation)

	def get_interfaces(self,bot,indicator):
		#returns all indicator interfaces
		interfaces = {}
		interfaces2 = []
		for i,interface in enumerate(bot.indicators[indicator].indicatorInterface):

			interfaces[i] = {'title': interface.title, 'value': interface.value, 'options': interface.options, 'step':interface.step}
			# interfaces[i] = [{(str(x) for x in list(inteface.keys()):interface[x]} for x in interface}]
			keys = interfaces.keys()
			interfaces2.append({'title': interface.title, 'value': interface.value, 'options': interface.options, 'step': interface.step})
		# interfaces2[i] = [
			# {str(x): bot.indicators[indicator].indicatorInterface[x]} for x in indicator]
		return interfaces, interfaces2




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
			index = []
			for d in data_dict:
					index.append(pd.to_datetime(d['T'], unit='s'))

			df = pd.DataFrame(data_dict, index=index)
			print(df)
			return df

	def to_df_for_ta(self, market_history):

		market_data = [
			{

				"D": x.timeStamp,
				"O": x.open,
				"H": x.highValue,
				"L": x.lowValue,
				"C": x.close,
				"B": x.currentBuyValue,
				"S": x.currentSellValue,
				"V": x.volume,
			}
			for x in market_history
		]

		df = pd.DataFrame(market_data)
		df['D'] = pd.to_datetime(df['D'])
		df.set_index(pd.DatetimeIndex(df['D']))
		print(df.index)
		return df
	def get_all_markets(self):

		markets = [
			(
				EnumPriceSource(i.priceSource).name,
				i.primaryCurrency,
				i.secondaryCurrency,
				i,
			)
			for i in self.c.marketDataApi.get_all_price_markets().result
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
			marketdata = self.c.marketDataApi.get_history_from_market(
				priceMarketObject, interval, depth)
			if marketdata.errorCode != 'SUCCESS':
				for r in range(2):
					print(marketdata.errorCode.value, marketdata.errorMessage)
					marketdata = self.c.marketDataApi.get_history_from_market(
										priceMarketObject, interval, depth)
			else:
				df = self.to_df_for_ta(marketdata.result)
				print(df)

				return df


class BackTesting(Haas):
	def __init__(self):
		Haas.__init__(self)

	def iterate_indicator(self, indicator, bot):

		interfaces = self.get_interfaces(indicator)
		bt_range = self.dfine_bt_range(indicator)
		for i, interface in enumerate(interfaces):
			resbrute = optimize.brute(get_bt_reults, bt_range,args=(bot,indicator),full_output=True,finish=optimize.fmin)



	def setup_indicator(self,bot,indicator,param,value):
			change = self.c.tradeBotApi.edit_bot_indicator_settings(
				bot.guid, indicator.guid, param, value)
			if change.result:
				print('Sucessfuy changed indicator parameters')
			else:
				print(change.errorCode, change.errorMessage)

	def backtest_bot(self,bot):
			bt = self.c.tradeBotApi.backtest_trade_bot(bot.guid, iiv.total_ticks())
			if bt.result:
				return bt.result

	def get_bt_results(self, bot, indicator, param, value):
		self.setup_indicator(self, bot, indicator, param, value)
		bt = backtest_bot(self, bot)
		return bt.roi


	def dfine_bt_range(self, indicator):
		for interface in indicator:
			if interface.options != None:
				if interface['value'] <= interface['step']:
					bt_range = (interface['step'],
									interface['value'] + interface['step']*10, interface['step'])
					return bt_range

				elif interface['value'] >= interface['step'] * 100:
					bt_range=(interface['value']-interface['step']*10,
								interface['value'],interface['step'])
					return bt_range
			else:
				pass

	def memoize(func):
   	 cache = dict()

    # def memoized_func(*args):
    #     if args in cache:
    #         return cache[args]
    #     result = func(*args)
    #     cache[args] = result
    #     return result

    # return memoized_func





def tradebotmain():
	h = TradeBot()
	bot = BotSellector().get_trade_bot()
	indicators = h.get_indicators(bot)
	indicator = h.select_indicator(indicators)
	# print(indicator.__dict__)
	interfaces = h.get_interfaces(bot, indicator.guid)[1]

	print(interfaces)


if __name__ == '__main__':
	tradebotmain()
