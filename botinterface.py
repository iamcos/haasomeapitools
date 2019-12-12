from haasomeapi.apis.MarketDataApi import MarketDataApi
from haasomeapi.apis.ApiBase import ApiBase
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from haasomeapi.enums.EnumCustomBotType import EnumCustomBotType
from haasomeapi.HaasomeClient import HaasomeClient
from haasomeapi.dataobjects.marketdata.Market import Market
from haasomeapi.dataobjects.custombots.BaseCustomBot import BaseCustomBot
import pandas as pd
from haasomeapi.apis.AccountDataApi import AccountDataApi
import configserver
from time import sleep
import jsonpickle
from botdatabase import BotDB
from sqlalchemy import create_engine
import json

import sqlite3 as sqllite
from datetime import datetime
from multiprocessing import Lock, Process, Queue, current_process
import queue
from multiprocessing.dummy import Pool
import grequests
import requests
import asyncio
import time
from typing import Any, Iterable, List, Tuple, Callable
import os
import aiohttp
import requests

class BotInterface:
	def __init__(self):
		self.connection_string = configserver.validateserverdata()
		self.connect = HaasomeClient(
			self.connection_string[0], self.connection_string[1]
		)
		self.markets = self.get_all_markets()
		self.selectedbot = None
		self.depth = 1000
		self.interval = 1
		self.sqllite_memory = sqllite.connect(":memory:")
		self.sqllite = sqllite.connect("market.db")
		self.custombots = self.get_custombots()
		self.tradebots = self.get_tradebots()
		self.enabledaccounts = self.get_enabled_accounts()

	def get_custombots(self):
		bots = [[i.name, i, i.guid, i.roi] for i in self.connect.customBotApi.get_all_custom_bots().result]
		# print(bots)

		bots3 = [[i.name,jsonpickle.encode(i)]
			for i in self.connect.customBotApi.get_all_custom_bots().result]
		bots2 = [
			{"name": i.name, "bot": i, "guid": i.guid}
			for i in self.connect.customBotApi.get_all_custom_bots().result
		]
		df = pd.DataFrame(bots, columns=(["name", "obj", "guid", "roi"]))
		print(df)
		return bots, df, bots2,bots3

	def return_customBot_object_by_guid(self,guid):
		print('guid',guid)
		bot = [i for i in
			 self.connect.customBotApi.get_all_custom_bots().result if i.guid == guid]
		# print(bot)
		return bot[0]


	def get_enabled_accounts(self):
		accounts = [
			[
				i[1].name,
				EnumPriceSource(i[1].connectedPriceSource),
				i[1].isSimulatedAccount,
				i[1].guid,
				i[1].platformType,
			]
			for i in self.connect.accountDataApi.get_all_account_details().result.items()
		]
		df = pd.DataFrame(
			accounts,
			columns=[
				"name",
				"connectedPriceSource",
				"simulated",
				"guid",
				"platformType",
			],
		)

		return accounts

	def get_all_markets(self):

		markets = [
			(
				EnumPriceSource(i.priceSource).name,
				i.primaryCurrency,
				i.secondaryCurrency,
				i,
			)
			for i in self.connect.marketDataApi.get_all_price_markets().result
		]


		df = pd.DataFrame(
			markets,
			columns=(["pricesource", "primarycurrency",
					 "secondarycurrency", "obj"]),
		)
		return df

	def get_allbots(self):
		all_bots = []
		for bot in self.custombots:
			all_bots.append(bot)

		for bot in self.tradebots:
			all_bots.append(bot)
		return all_bots

	def return_priceMarket_object(self, df, pricesource, primarycoin, secondarycoin):
		'''
			Returns priceSource object for given pricesorce, primarycoin, secondarycoin if that pricesource is enabled in Haas.
		'''

		obj = df[df["pricesource"] == pricesource][df["primarycurrency"] == primarycoin][df["secondarycurrency"] == secondarycoin].values

		return obj[0][3]

	def execute_price_api_request(self,pricesource, primarycoin, secondarycoin):
		request_url = f'http://price-api.haasonline.com/PriceAPI.php?channel=LASTMINUTETICKS_{pricesource}_{primarycoin}_{secondarycoin}_'

		markets = self.get_pricemarkets_for_market(pricesource, primarycoin, secondarycoin)
		for row in markets.iterrows():
			url = f'http://price-api.haasonline.com/PriceAPI.php?channel=LASTMINUTETICKS_{pricesource}_{primarycoin}_{secondarycoin}_'
			with requests.Session() as s:
				resp = s.get(url)

				return resp

	def download_all(urls: Iterable[str]) -> List[Tuple[str, bytes]]:
		def download(url: str) -> Tuple[str, bytes]:
			print(f"Start downloading {url}")
			with requests.Session() as s:
				resp = s.get(url)
				out= image_name_from_url(url), resp.content
			print(f"Done downloading {url}")
			return out
		return [download(url) for url in urls]

	def get_market_data(self,priceMarketObject, interval, depth):
			count = 0
			marketdata = self.connect.marketDataApi.get_history_from_market(
				priceMarketObject, interval, depth)
			sleep(5)
			print(marketdata.errorCode, marketdata.errorMessage)
			# print(marketdata.errorCode, marketdata.errorMessage,marketdata.result))
			print(f'working on market history, for {priceMarketObject.primaryCurrency}{priceMarketObject.secondaryCurrency}with interval {interval} for {depth} depth')
			while marketdata.errorCode.value == EnumErrorCode.PRICE_MARKET_IS_SYNCING and depth > 0:
				print(marketdata.errorCode.value, marketdata.errorMessage)
				sleep(5)
				marketdata = self.connect.marketDataApi.get_history_from_market(
				priceMarketObject, interval, depth)
			else:
				print(marketdata.errorCode)

			while marketdata.errorCode == EnumErrorCode.SUCCESS:

				if len(marketdata.result) >0 :
					print('history is ', len(marketdata.result),' long')

					df = self.to_df_for_ta(marketdata.result)
					print(df)
					return df
			else:
				print(marketdata.errorCode)




	def read_db(self, market):
		market=self.markets[market]
		pd=df.read_sql(
			str(market.priceSource, market.primaryCurrency,
				market.secondaryCurrency),
			self.db,
		)
		return pd

	def save_state(self):
		frozen=jsonpickle.encode(self)
		with open("state.haas", "w") as f:
			json.dump(frozen, f)
		# print(f'Current state of operations has been saved to file state.haas')

	def load_state(self):
		with open("state.haas", "r") as f:
			self=json.load(f)
		# print(self.__init__, 'has been loaded back into the memory')

	def get_ticks(start_date, end_date, bot):

		# print(start_date,end_date)
		end = dt.fromisoformat(end_date)
		start = dt.fromisoformat(start_date)
		seconds = end - start
		# print(int(seconds.total_seconds()))
		return int(seconds.total_seconds())

	def to_df(self,market_history):

		market_data = [
			{
				"timeStamp": x.timeStamp,
				"unixTimeStamp": pd.to_datetime(x.unixTimeStamp, unit="s"),
				"open": x.open,
				"highValue": x.highValue,
				"lowValue": x.lowValue,
				"close": x.close,
				"volume": x.volume,
				"currentBuyValue": x.currentBuyValue,
				"currentSellValue": x.currentSellValue,
			}
			for x in market_history
		]

		df = pd.DataFrame(market_data)
		return df

	def to_df_for_ta(self,market_history):

		market_data = [
			{

				"date": x.timeStamp,
				"open": x.open,
				"high": x.highValue,
				"low": x.lowValue,
				"close": x.close,
				"volume": x.volume,
				"buy": x.currentBuyValue,
				"sell": x.currentSellValue,
			}
			for x in market_history
		]

		df = pd.DataFrame(market_data)
		return df

	def df_to_csv(self,df, marketobj,interval):

		filename = f'{EnumPriceSource(marketobj.priceSource).name},{marketobj.primaryCurrency},{marketobj.secondaryCurrency},{interval}.csv'

		df.to_csv(filename, index_label= 'index')
		print("Market History Sucessfuly Saved to CSV")

	def csv_to_df(filename):

		data = pd.read_csv(filename)

		return data
		df.to_csv(filename)
		print("Market History Sucessfuly Saved to CSV")

	def get_tradebots(self):

		bots = [
			[i.name, i.guid, i]
			for i in self.connect.tradeBotApi.get_all_trade_bots().result
		]
		bots2 = [
			{i.name: i} for i in self.connect.tradeBotApi.get_all_trade_bots().result
		]
		bot_dict = [{"id": i, "label": b[0], "value": b[1]}
					for i, b in enumerate(bots)]

		df = pd.DataFrame(bots, columns=(["name", "guid", "obj"]))
		# print(f'\Trade Bots:\n {df}[1]')

		# print(df.completedOrders)
		# print(cb[0][1])
		return bots, df, bot_dict, bots2

	def save_market_history_to_database(self, market, primarycoin, secondarycoin, interval, depth):
		marketobj = self.return_priceMarket_object(self.markets, market, primarycoin, secondarycoin)
		market_history = self.get_market_data(marketobj, interval, depth)

		db_name = 'market.db'
		engine = create_engine("sqlite:///%s" % db_name,
							   execution_options={"sqlite_raw_colnames": True})
		table_name = f'{EnumPriceSource(marketobj.priceSource).name},{marketobj.primaryCurrency},{marketobj.secondaryCurrency},{interval}'
		# market_history.to_csv(f'{table_name}.csv')
		market_history.to_sql(
			table_name, con=engine, if_exists='append')
		return market_history

	def get_market_history_from_database(self, market, primarycoin, secondarycoin,interval):
		marketobj = self.return_priceMarket_object(
			self.markets, market, primarycoin, secondarycoin)
		db_name = 'market.db'
		table_name = f'{EnumPriceSource(marketobj.priceSource).name},{marketobj.primaryCurrency},{marketobj.secondaryCurrency}'
		engine = create_engine("sqlite:///%s" % db_name,execution_options={"sqlite_raw_colnames": True})
		market_history = pd.read_sql_table(table_name,engine)
		# print(market_history)
		return market_history

	def update_market_history_csv(self, market, primarycoin, secondarycoin, interval, depth):
		marketobj = self.return_priceMarket_object(
			self.markets, market, primarycoin, secondarycoin)
		filename = f'{EnumPriceSource(marketobj.priceSource).name},{marketobj.primaryCurrency},{marketobj.secondaryCurrency},{interval}.csv'
		print(filename)
		ta = pd.read_csv(filename)
		last = ta.iat[-1, 1]
		last = pd.to_datetime(last)
		print(last)


		calculated_interval = pd.to_datetime(
			ta.iat[-1, 1]) - pd.to_datetime(ta.iat[-2, 1])
		calculated_interval = int(calculated_interval.total_seconds() /60/interval)
		time_with_no_history = datetime.now() - last
		time_with_no_history = time_with_no_history.total_seconds()/60/interval
		print(time_with_no_history)
		print(f'{last} - {datetime.now()} = {time_with_no_history}')


		# print(calculated_interval)

		print(f' There is no history in database for {time_with_no_history} since last record.')
		ticks_to_get = time_with_no_history/calculated_interval
		# print(ticks_to_get)
		missing_data = self.get_market_data(marketobj, interval, int(time_with_no_history))
		# print(missing_data)

		ta2 = pd.merge_ordered(ta, missing_data, left_by='date')
		# print(ta2)
		ta2.to_csv(filename)

	def get_pricemarkets_for_market(self, market, primarycoin=None, secondarycoin=None):

		df = self.markets
		if primarycoin == None and secondarycoin == None:

			obj = df[df["pricesource"] == market]
		elif primarycoin != None:
			obj = df[df["pricesource"] == market][df["primarycurrency"]
											  == primarycoin]
		elif secondarycoin != None:
			obj = df[df["pricesource"] == market][df["secondarycurrency"] == secondarycoin]

		return obj
		# print(obj)

	def dl_history_for_markets(self, obj, interval, depth, primarycoin=None, secondarycoin=None):

			for row in obj.iterrows():
				print(row[1]['pricesource'], row[1]
					['primarycurrency'], row[1]['secondarycurrency'])
				marketobj = self.return_priceMarket_object(
								self.markets, row[1]['pricesource'], row[1]['primarycurrency'], row[1]['secondarycurrency'])
				market_data = self.get_market_data(marketobj, 30, 50)

				db_name = 'ta.db'
				engine = create_engine("sqlite:///%s" % db_name,
									execution_options={"sqlite_raw_colnames": True})
				table_name = f'{EnumPriceSource(marketobj.priceSource).name},{marketobj.primaryCurrency},{marketobj.secondaryCurrency},{interval}'
				# market_history.to_csv(f'{table_name}.csv')
				try:
					market_data.to_sql(table_name, con=engine, if_exists='append')
				except AttributeError:
					pass



		# # # print(dict.keys())
		# nxt = next(obj.iterrows())[1]
		# print(nxt)

		# print(ticks_to_get)


	def save_market_history_to_csv(self, market, primarycoin, secondarycoin, interval, depth):
		'''
		Save to csv market history of given depth (ticks) in a given interval(candle interval), for market being 'BINANCE'/'DERBIT' and so on, for primarycoin('BTC'), secondarycoin ('ETH').
		to initialize this command, we first create an instance of BotInterface class as:
		haas = BotInterface()
		Follwowing the creation comes save to csv file command:
		haas.save_market_historu_to_csv()
		Inside the ()at the end of this command  are written our variables: 'BINANCE', 'BTC','USDT' for market and coin pair, 15 is candle interval and 1000 - ticks. So we should end up with a file containing 1000 candles of 15 minutes each with all the data Haasapi is capable of providing.
		This file can then be used in other applications like plotting, analyzing, applying technical indicators to, machine learning and so forth.
		'''
		marketobj = self.return_priceMarket_object(self.markets,market, primarycoin, secondarycoin)
		market_history = self.get_market_data(marketobj, interval, depth)
		self.df_to_csv(market_history, marketobj,interval)
		return market_history



def main():
	try:
		haas = BotInterface()
		# haas.save_market_history_to_csv('BINANCE', 'BTC', 'USDT', 1, 100)
		# haas.save_market_history_to_database('BINANCE', 'BTC', 'USDT', 15, 1000)
		# td = haas.get_market_history_from_database('BINANCE', .'BTC', 'USDT',15)

		market = 'BINANCE'
		primarycoin = 'BTC'
		secondarycoin = 'USDT'
		d = haas.execute_price_api_request(market, primarycoin, secondarycoin)

		# print(d.text)
		# for v in d.content:
		# 	# print(k)
		# 	print(v)
		df = jsonpickle.decode(d.text)
		# for x in df:
		# help(df)
		print(pd.to_json(df))
		# df2 = pd.DataFrame(df1)
		df2.reindex
		# print(df2)
		for x, y in df.items():
			df = x
		hey = df2['Data'].to_dict()
		df3 = pd.read_dict((hey))
		na = pd.melt(df3)
		print(na)



		# result = await co_mp_apply(haaas.get_multimarket_data(market, args=(market, 5, 100, 'BTC'))

		# task = background_task(haas.get_multimarket_data)(market, 5, 100, 'BTC')
		# wait_completed(taskn
		# result = a1.run(haas.get_multimarket_data(15))
		# haas.get_multimarket_data(market, 5, 100, secondarycoin=secondarycoin)
		# marketobj = haas.return_priceMarket_object(
		#             haas.markets, market, primaryco,in, secondarycoin)
		# filename = f'{EnumPriceSource(marketobj.priceSource).name},{marketobj.primaryCurrency},{marketobj.secondaryCurrency}.csv'
		# td.to_csv(filename)
		# haas.update_market_history_csv(
		# 	market, primarycoin, secondarycoin, 1, 100)
		# ta = pd.read_csv(filename)
		# interval = pd.to_datetime(ta.iat[-1, 2])- pd.to_datetime(ta.iat[-2, 2])
		# print(pd.to_datetime(ta.iat[-1, 2]), pd.to_datetime(ta.iat[-2, 2]),interval.total_seconds()/60)
		# print(con.markets)
		# for i in con.markets:
		# print(i)
		# mo = con.return_priceMarket_object(con.markets, "BINANCE", "BTC", "USDT")
		# print(mo)
		# market_data = con.get_market_data(mo)
		# bot = con.return_customBot_object('0cf0a9d7-e719-4f17-9704-adc05456b036')
		# print(bot.priceMarket.priceSource)
		# print(more)

		# print(data)
		# print(b['priceSource']())
		# print()
		# for i in list(b.keys())[:3]:
		#     print(b[i])
	except KeyboardInterrupt:
		print("Interrupted")
		try:
			con.save_state
		except SystemExit:
			raise


if __name__ == "__main__":
	main()
