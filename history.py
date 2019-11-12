from __future__ import print_function

import csv
from datetime import datetime
import time
# from pathlib import Path
import os
import haasomeapi.enums.EnumErrorCode as EnumErrorCode
import ipywidgets as widgets
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly as py
import plotly.graph_objects as go
import spicy as special
from haasomeapi.enums.EnumCustomBotType import EnumCustomBotType
from haasomeapi.enums.EnumOrderType import EnumOrderType
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
from haasomeapi.HaasomeClient import HaasomeClient
from ipywidgets import fixed, interact, interact_manual, interactive

import botsellector
import init
import interval as iiv
# import rotator
from botdatabase import BotDB

matplotlib.style.use('ggplot')



# py.offline.init_notebook_mode(connected = True)
haasomeClient = init.connect()


def get_specific_market():
	markets = {}
	all_price_sources = haasomeClient.marketDataApi.get_enabled_price_sources().result
	primarycurrency = []
	secondarycurrency = []
	pairs = []
	for i,market in enumerate(all_price_sources):
		# markets[market] = haasomeClient.marketDataApi.get_price_markets(21).result
		markets[market] = haasomeClient.marketDataApi.get_price_markets(EnumPriceSource[market.upper()]).result
		print(i, market)
	user_input = int(input('Type market number to select'))
	market = all_price_sources[user_input]
	for market in markets[market]:
		if market.secondaryCurrency not in secondarycurrency:
			secondarycurrency.append(market.secondaryCurrency)
		if market.primaryCurrency not in primarycurrency:
			primarycurrency.append(market.primaryCurrency)
		if market.secondaryCurrency and market.primaryCurrency not in pairs:
			pairs.append([market.secondaryCurrency, market.primaryCurrency, market.contractName])
	print(pairs)



def get_market_data(bot):
	orders = sorted(bot.completedOrders, key=lambda x: x.unixAddedTime, reverse=True)
	print('Order Dates: ', [x.unixAddedTime for x in orders])
	ticks = int(iiv.total_ticks(bot))
	market_history_request = haasomeClient.marketDataApi.get_history(
		bot.priceMarket.priceSource,
		bot.priceMarket.primaryCurrency,
		bot.priceMarket.secondaryCurrency,
		bot.priceMarket.contractName,
		bot.interval,
		ticks)
	# print(ticks)
	print('downloading history for ', bot.priceMarket.primaryCurrency, bot.priceMarket.secondaryCurrency)
	print(market_history_request.errorCode.value)
	if market_history_request.errorCode.value == 100:
		market_history = market_history_request.result
		if len(market_history_request.result) != 0:
			print(len(market_history_request.result), 'ticks of market history retrieved')
			return market_history
		else:
			print('But', len(market_history_request.result), 'means nothing was recieved' )
	else:
		print(market_history_request.errorCode, market_history_request.errorMessage)
		print('things did not go as planned. aborting')
	
def to_df(market_history):

	market_data = [{'timeStamp':x.timeStamp,'unixTimeStamp':pd.to_datetime(x.unixTimeStamp,unit='s'),'open':x.open,'highValue':x.highValue, 'lowValue':x.lowValue,'close':x.close,'volume':x.volume,'currentBuyValue':x.currentBuyValue,'currentSellValue':x.currentSellValue} for x in market_history]

	df = pd.DataFrame(market_data)
	# df = pd.DataFrame(market_history)
	# for index, row in df.iterrows():
	# 	print(row)
	return df

def df_to_csv(df, bot):
	ticks = int(iiv.int(bot))
	filename = (
		str(bot.priceMarket.primaryCurrency)
		+ "\\"
		+ str(bot.priceMarket.secondaryCurrency)
		+ " "
		+ str(ticks)
		+ ".csv")
	df.to_csv(filename)
	print('Market History Sucessfuly Saved to CSV')

def csv_to_df(filename):
	data = pd.read_csv(filename)
	# data.reset_index( inplace=True)
	# data.set_index(['primarycoin','secondarycoin','interval','rsil', 'rsib', 'rsis', 'bbl', 'devup', 'devdn'], inplace=True)
	# data.sort_index(inplace=True)
	# print(data.head(20))
	# print(data.tail(20))
	return data

def orders_to_df(bot):

	#turns completed orders to dataframe. If bot has no orders then returns
	if len(bot.completedOrders) > 0:
		try:
			completedOrders = [{'pair': (x.pair.primaryCurrency, x.pair.secondaryCurrency), 'orderId':x.orderId,'orderStatus':x.orderStatus, 'orderType':x.orderType, 'price': x.price,'amount':x.amount,'amountFilled':x.amountFilled,'unixTimeStamp':pd.to_datetime(x.unixAddtoredTime,unit='s')} for x in bot.completedOrders]
			orders_df = pd.DataFrame(completedOrders)
		except AttributeError:
			completedOrders = [{'pair': None, 'orderId': None,'orderStatus':None, 'orderType':None, 'price': None,'amount':None,'amountFilled':None,'unixTimeStamp':datetime.today()}for x in range(1)]
			orders_df = pd.DataFrame(completedOrders)

	else:
		completedOrders = [{'pair': None, 'orderId': None,'orderStatus':None, 'orderType':None, 'price': None,'amount':None,'amountFilled':None,'unixTimeStamp':datetime.today()}for x in range(1)]
		orders_df = pd.DataFrame(completedOrders)
	return orders_df

# def backtest_bots(bot):
# 	results, bot_object_list  = rotator.backtestingfrommemory(bot, haasomeClient)
# 	return bot_object_list


def combine_orders_with_history(df, orders_df):
	#does what it says - combines into a single dataframe orders and history for future use. 
	history_with_orders = pd.merge(df,orders_df,how = 'left', on = 'unixTimeStamp')
	# history_with_orders['unixTimeStamp'] = pd.to_datetime(history_with_orders['unixTimeStamp'])

	return history_with_orders

def calculate_profit_lables(orders_df):
	print(orders_df)
	for index, row in orders_df.iterrows():
	
			if orders_df.loc[index,'orderType'] == 0:
				if orders_df.loc[index, 'price'] != 0:
					orders_df.loc[index,'profit'] = orders_df.loc[index, 'price'] + orders_df.loc[str(int(index) - 1), 'price']
			else:
				try:
					orders_df.loc[index,'profit'] = orders_df.loc[index, 'price'] - orders_df.loc[str(int(index) - 1), 'price']
				except KeyError:
					pass
	print(orders_df)
	return orders_df



def plot_bot_trades(history_with_orders):
		plt.figure()
		history_with_orders.plot(kind='line', x = 'unixTimeStamp', y = [ 'price', 'currentBuyValue']) 
		fig = go.Figure(data=[go.Candlestick(x=history_with_orders['unixTimeStamp'],
			open=history_with_orders['open'],
			high=history_with_orders['highValue'],
			low=history_with_orders['lowValue'],
			close=history_with_orders['close'])])
		fig.add_trace(go.Scatter(x=history_with_orders['unixTimeStamp'],y=history_with_orders['price'], mode = 'markers', name='markers',marker_color='rgba(0, 152, 26, 1.8)'))
		fig.show()

def plot_bots(botlist):
	botlist = sorted(botlist,key=lambda x: len(x.completedOrders), reverse=True)
	market_history = get_market_data(botlist[0])
	# for bot in botlist:
	# 	print(len(bot.completedOrders))
	
	mh_df = to_df(market_history)
	plt.figure()
	
	mh_df.plot(kind='line', x = 'timeStamp', y = 'currentBuyValue')
	fig = go.Figure(data=[go.Candlestick(x=
	['timeStamp'],
		open=
		['open'],
		high=mh_df['highValue'],
		low=mh_df['lowValue'],
		close=mh_df['close'])])
	for i,bot in enumerate(botlist):
		orders_df = orders_to_df(bot)
		fig.add_trace(go.Scatter(x = orders_df['unixTimeStamp'], y = orders_df['price'], mode = 'markers', marker = dict(size=20), name = str(i)+ ' '+str(bot.roi)+'  ROI '))

	fig.show()
	for bot in botlist:
		plt.figure()
		mh_df 

def bot_to_plot(bot):
	#Gets market history, turns it into data frame, then does the same for bot orders and plots it on a graph
	market_history = get_market_data(bot)
	mh_df = to_df(market_history)
	orders = orders_to_df(bot)
	orders_ticks = combine_orders_with_history(mh_df, orders)
	# plot_bot_trades(orders_ticks)
	plot_bot_trades(orders_ticks)
# 	return frames, mh_df


def botlist_orderbook_combine_with_market_ticks(botlist):
	market_history = get_market_data(botlist[0])
	histories_with_orders = []
	mh_df = to_df(market_history)
	for bot in botlist:
		orders = orders_to_df(bot)
		orders_ticks = combine_orders_with_history(mh_df, orders)
		histories_with_orders.append([bot.roi,orders_ticks])
	return histories_with_orders

def return_file():
	path_to_db_files = './'
	files = []
	for file in os.listdir(path_to_db_files):
		if file.endswith(".csv"):
			files.append(os.path.join(path_to_db_files, file))
	for i, file in enumerate(files):
		print(i, file)
	userinput = input('Type file number to select it:  ')
	return files[int(userinput)]

def main():
	botfile = BotDB.return_botlist_file()
	botlist = BotDB.load_botlist(botfile)
	print('HELLO',[x.roi for x in botlist])
	plot_bots(botlist)
def main8():
	
	filename = return_file()
	csv = pd.read_csv(filename)
	

	print(csv)

if __name__ == "__main__":
	main()

	