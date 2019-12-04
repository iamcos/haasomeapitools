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
import init
from time import sleep
import jsonpickle
from botdatabase import BotDB
from sqlalchemy import create_engine
import json
import sqlite3 as db

"""
BotInterface allows for easy access and manipulation of HaasomeAPI protocols:
	Get:
		all bots
		all markets
	Retrieve :
		market object with pricesource, primary coin and secondary coin parameters.
		Custom Bot Object by guid
	Prepare:
		Price-tick data

	Some functions have multipe outputs, even suitable for Dash by plotly.

	Save and load current data state to disk.
	Store and load market data to CSV

"""


class BotInterface:
	def __init__(self):
		self.connection_string = configserver.validateserverdata()
		self.connect = HaasomeClient(
			self.connection_string[0], self.connection_string[1]
		)
		self.markets = self.get_all_markets()
		self.selectedbot = None
		self.depth = 0
		self.interval = 1
		self.db = db.connect(":memory:")
		self.custombots = self.get_custombots()
		self.tradebots = self.get_tradebots()
		self.enabledaccounts = self.get_enabled_accounts()

	def get_custombots(self):
		bots = [[i.name, i, i.guid, i.roi] for i in self.connect.customBotApi.get_all_custom_bots().result]


		bots3 = [[i.name,jsonpickle.encode(i)]
			for i in self.connect.customBotApi.get_all_custom_bots().result]
		bots2 = [
			{"name": i.name, "bot": i, "guid": i.guid}
			for i in self.connect.customBotApi.get_all_custom_bots().result
		]
		df = pd.DataFrame(bots, columns=(["name", "obj", "guid", "roi"]))
		print(df)
		return bots, df, bots2,bots3

	def return_customBot_object(self,guid):
		print('guid',guid)
		bot = [i for i in
			 self.connect.customBotApi.get_all_custom_bots().result if i.guid == guid]

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



	def get_market_data(self,priceMarketObject, interval, depth):
			count = 0
			marketdata = self.connect.marketDataApi.get_history_from_market(
				priceMarketObject, interval, depth)
			sleep(5)
			print(marketdata.errorCode, marketdata.errorMessage)

			print(f'working on market history, for {priceMarketObject.primaryCurrency}{priceMarketObject.secondaryCurrency}with interval {interval} for {depth} depth')
			while marketdata.errorCode.value != 'SUCCESS' and marketdata.errorCode.value != 'PRICE_MARKET_IS_SYNCING' and depth > 0:
				print(marketdata.errorCode, marketdata.errorMessage)
				sleep(5)

				marketdata = self.connect.marketDataApi.get_history_from_market(
				priceMarketObject, interval, depth)

				if len(marketdata.result) >0 :
					print('history is ', len(marketdata.result),' long')

					df = self.to_df_for_ta(marketdata.result)
					return df
				return df
				break






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

	def df_to_csv(df, bot):

		#Save Dataframe to CSV
		ticks = int(iiv.int(bot))
		filename = (
			str(bot.priceMarket.primaryCurrency)
			+ "\\"
			+ str(bot.priceMarket.secondaryCurrency)
			+ " "
			+ str(ticks)
			+ ".csv"
		)
		df.to_csv(filename)
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


def main():
	try:

		con=BotInterface()


	except KeyboardInterrupt:
		print("Interrupted")
		try:
			con.save_state
		except SystemExit:
			raise


if __name__ == "__main__":
	main()
