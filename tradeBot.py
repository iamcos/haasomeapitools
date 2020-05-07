from haasomeapi.apis.TradeBotApi import TradeBotApi
from haasomeapi.dataobjects.custombots.dataobjects.Indicator import Indicator
from haasomeapi.dataobjects.custombots.dataobjects.IndicatorOption import (
    IndicatorOption,
)
from haasomeapi.dataobjects.custombots.dataobjects.Insurance import Insurance
from haasomeapi.dataobjects.custombots.dataobjects.Safety import Safety
from haasomeapi.enums.EnumErrorCode import EnumErrorCode

from haasomeapi.enums.EnumCoinPosition import EnumCoinPosition
from haasomeapi.enums.EnumLimitOrderPriceType import EnumLimitOrderPriceType
import interval as iiv
import configserver
import haasomeapi.enums.EnumIndicator2 as EnumIndicator
import numpy as np
import pandas as pd
import time
import botsellector
import multiprocessing as mp
from decimal import Decimal
from haasomeapi.HaasomeClient import HaasomeClient
ip, secret = configserver.validateserverdata()
haasomeClient = HaasomeClient(ip, secret)

def multiprocess(bot, guid):
    newbotname = bot.name + " " + bot.indicators[guid].indicatorTypeShortName + " temp"
    newbot = haasomeClient.tradeBotApi.clone_trade_bot(
        bot.accountId,
        bot.guid,
        newbotname,
        bot.priceMarket.primaryCurrency,
        bot.priceMarket.secondaryCurrency,
        bot.priceMarket.contractName,
        bot.leverage,
        False,
        False,
        False,
        True,
        True,
    ).result
    cloeindicator = haasomeClient.tradeBotApi.clone_indicator(
        bot.guid, guid, newbot.guid
    ).result

    gettradebot = haasomeClient.tradeBotApi.get_trade_bot(newbot.guid).result
    for guid in gettradebot.indicators:
        # print('Indicator name: ',gettradebot.indicators[guid].indicatorTypeShortName)
        for i, options in enumerate(
            gettradebot.indicators[str(guid)].indicatorInterface
        ):
            indicators.append(i)
        for interface in gettradebot.indicators[str(guid)].indicatorInterface:
            # print(interface.title, interface.value , interface.options)
            print(interface.value.type)


def new_bot_for_every_indicator(haasomeClient, bot, interval):
    ticks = iiv.readinterval(1)
    newbots = []
    createdbots = []
    indicators = []
    options = []

    for guid in bot.indicators:
        newbotname = (
            bot.name + " " + bot.indicators[guid].indicatorTypeShortName + " temp"
        )
        newbot = haasomeClient.tradeBotApi.clone_trade_bot(
            bot.accountId,
            bot.guid,
            newbotname,
            bot.priceMarket.primaryCurrency,
            bot.priceMarket.secondaryCurrency,
            bot.priceMarket.contractName,
            bot.leverage,
            False,
            False,
            False,
            True,
            True,
        ).result
        cloeindicator = haasomeClient.tradeBotApi.clone_indicator(
            bot.guid, guid, newbot.guid
        ).result
        newbots.append(newbot)
    return newbots


def get_indicators(bot):
    #returns all tradebot indicators
    indicators = {}
    for indicator in bot.indicators:
        indicators[bot.indicators[indicator].indicatorTypeShortName] = indicator
    return indicators

def select_indicator(indicators):
    #returns user selected indicator of a trade bot
    keys = list(indicators.keys())
    print(indicators.keys())
    for i, indicator in enumerate(keys):
        print(i, indicator)
    response = input('Type indicator number to select it: ')
    # print(keys[int(response)])
    # print(indicators[response])
    print(indicators[str(keys[int(response)])])
    return indicators[str(keys[int(response)])]



def get_interfaces(bot, indicator):
    #returns all indicator interfaces
    # interfaces = {}
    interfaces = {}
    # for indicator in bot.indicators[indicator].indicatorInterface:
    for i,indicator in enumerate(bot.indicators[indicator].indicatorInterface):
        # print(indicator.title, indicator.value, indicator.options)
        interfaces[i] = {'title':indicator.title, 'value':indicator.value, 'options':indicator.options}
    # print(interfaces)
    return interfaces

def select_interface(bot, interfaces):
    #returns selected by user interface
    interface = {}
    # print(interfaces)
    for i, interface in enumerate(interfaces):
        print(interface, '.',interfaces[i]['title'],':', interfaces[i]['value'])
    response = input('Type parameter number to select it: ')
    # print(interfaces[int(response)])
    print(bot.indicators[indicator].indicatorInterface[int(response)])

def add_indicator(bot, indicator):
    try:
        add = haasomeClient.tradeBotApi.add_indicator(bot.guid, indicator)

        print(add.errorCode, add.errorMessage)
        try:
            print(EnumIndicator.EnumIndicator(indicator))
        except:
            print('something didnt work out')

    except ValueError or KeyError:
        pass

def get_indicator_interfaces_for_df(bot):
	indicators = {}
	interfaces ={}
	indicator_ranges_by_name ={}
	interface_ranges_by_name = {}
	indicators_with_ranges = {}


	dataframes = {}


	for ii, v in enumerate(bot.indicators):
		interfaces ={}
		index = []
		values = []
		print('\n',bot.indicators[v].indicatorTypeShortName)
		# indicators[ii] = v
		for i,vv in enumerate(bot.indicators[v].indicatorInterface):
			print(i,vv.title, vv.value, vv.options)
			interfaces[vv.title] = vv.value
			indicators[v] = interfaces
			index.append(vv.title)
			values.append(vv.value)
def to_dataframe(bot):
    interfaces = get_indicator_interfaces_for_df(bot)
    # print(interfaces)
    df = pd.DataFrame.from_dict(interfaces, orient="index")
    print(df)


def backtest_single_indicator_bot(bot):
    results = []
    indicators = get_indicator_interfaces_for_df(bot)

def printerrors(variable):
    print(variable.errorCode, variable.errorMessage)



def main1():
    pool = mp.Pool(mp.cpu_count())
    bot = botsellector.getalltradebots(haasomeClient)
    intt = get_indicator_interfaces_for_df(bot)
    # dd = to_dataframe(bot)

def add_all_indicators_to_bot():

    bot = botsellector.get_trade_bot(haasomeClient)
    for x in range(71):
        add_indicator(bot, x)

def main2():
    bot = botsellector.getalltradebots(haasomeClient)
    indicators = get_indicators(bot)
    indicator_guid = select_indicator(indicators)
    # print(indicator_guid)
    interfaces = get_interfaces(bot, indicator_guid)
    interface = select_interface(bot, interfaces)

def main3():
    bot = botsellector.getalltradebots(haasomeClient)
    config_indicators(bot)

def config_indicators(bot):
    indicators = get_indicators(bot)
    for indicator in indicators:
        interfaces = get_interfaces(bot,indicators[indicator])
        # print(indicator, interfaces)
        print(indicator,'has ', len(interfaces),'interfaces: ',[interfaces[x]['value'] for x in [x for x in interfaces.keys()]])
        # print(indicator,'has ', len(interfaces),'interfaces: ',[x for x in [interfaces[x] for x in [x for x in interfaces.keys()]]])





if __name__ == "__main__":
    # add_all_indicators_to_bot()
    main3()
