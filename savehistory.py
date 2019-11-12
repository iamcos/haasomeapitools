import csv
import multiprocessing as mp
import os.path
import time
from pathlib import Path

import haasomeapi.enums.EnumErrorCode as EnumErrorCode
import numpy as np
import pandas as pd
from haasomeapi.enums.EnumCustomBotType import EnumCustomBotType
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
from haasomeapi.HaasomeClient import HaasomeClient

import botsellector
import configserver
import init
import interval as iiv
haasomeClient= init.connect()




def allenabledmarkets():
	priceSources = {}
	sources = haasomeClient.marketDataApi.get_enabled_price_sources().result
	
	for source in sources:
		print(source.capitalize())
		print(str(source).capitalize())
		print(source)
		print(EnumPriceSource(EnumPriceSource(str(source))))
		priceSources[str(source)] = haasomeClient.marketDataApi.get_price_markets((EnumPriceSource(source))).result
		print(priceSources)
	print(priceSources)
	return(priceSources)

def markets(bot):
	basebotconfig = haasomeClient.customBotApi.get_custom_bot(bot.guid, EnumCustomBotType.MAD_HATTER_BOT).result
	markets = haasomeClient.marketDataApi.get_price_markets(basebotconfig.priceMarket.priceSource).result
	return markets

def market_history(priceMarket, ticks, interval):
		saved = 0
		interval = interval
		nohistory = 0
		count = 0
		historystat = haasomeClient.marketDataApi.get_history_from_market(priceMarket,interval,ticks)
		if historystat.errorCode.value == 100:
				print(historystat.errorCode.name, historystat.errorMessage, priceMarket.primaryCurrency, priceMarket.secondaryCurrency)
				print(len(historystat.result))
				if len(historystat.result) > 0:
					marketdata = historystat.result
					print('Market price data aquired')
					return marketdata
		else:
			print('Market history status: ', historystat.errorCode)
			historystat = haasomeClient.marketDataApi.get_history_from_market(priceMarket,interval,ticks)


def get_market_history(priceMarket, ticks):
		saved = 0
		interval = 1
		nohistory = 0
		count = 0
		historystat = haasomeClient.marketDataApi.get_history_from_market(priceMarket,interval,ticks)
		if historystat.errorCode.value == 100:
				print(historystat.errorCode.name, historystat.errorMessage, priceMarket.primaryCurrency, priceMarket.secondaryCurrency)
				print(len(historystat.result))
				if len(historystat.result) > 0:
					marketdata = historystat.result
					filename = str(EnumPriceSource(priceMarket.priceSource).name)+'_'+str(priceMarket.primaryCurrency)+'_'+str (priceMarket.secondaryCurrency)+'_'+str(len(marketdata))+'_'+str(interval)+'.csv'
					currentfile = Path(str(filename))
					currentfile.touch()
					print(filename, 'has been saved!')
					with open(filename, 'w', newline='') as csvfile:
						fieldnames = ['timeStamp','unixTimeStamp','open','highValue','lowValue','close','volume','currentBuyValue','currentSellValue']
						csvwriter = csv.DictWriter(csvfile,fieldnames=fieldnames)
						csvwriter.writeheader()
						for tick in marketdata:
							csvwriter.writerow({'timeStamp': str(tick.timeStamp),'unixTimeStamp': str(tick.unixTimeStamp), 'open': float(tick.open), 'highValue':  float(tick.highValue), 'lowValue': float(tick.lowValue),'close' : float(tick.close),'volume': float(tick.volume),'currentBuyValue': str(tick.currentBuyValue),'currentSellValue': float(tick.currentSellValue)})
							saved +=1
							print(saved, 'ticks has been saved')
		else:
			print(historystat.errorCode)
			historystat = haasomeClient.marketDataApi.get_history_from_market(priceMarket,interval,ticks)
			time.wait()



def main():
	botlist = botsellector.return_all_mh_bots(haasomeClient)
	bot = botsellector.get_specific_bot(haasomeClient, botlist)


	ticks = int(iiv.readinterval(bot))
	priceMarkets = markets(bot)
	for priceMarket in priceMarkets:
		marketdata = get_market_history(priceMarket, ticks)
		

if __name__ == '__main__':
	main()
