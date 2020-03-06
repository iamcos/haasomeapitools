# from licensing.models import *
# from licensing.methods import Key, Helpers
import configparser
import csv
import datetime
import fileinput
import json
import logging
import multiprocessing
import operator
import os
import re
import sys
import threading
import time
from datetime import datetime
from decimal import Decimal
from inspect import getmembers
from pathlib import Path
from time import gmtime, sleep, strftime
from typing import List
from multiprocessing.pool import ThreadPool
import concurrent.futures
import history
from botinterface import BotInterface as botI
import pandas as pd
import numpy as np
from haasomeapi.apis.AccountDataApi import AccountDataApi
from haasomeapi.apis.ApiBase import ApiBase
from haasomeapi.apis.MarketDataApi import MarketDataApi
from haasomeapi.dataobjects.accountdata.BaseOrder import BaseOrder
from haasomeapi.dataobjects.custombots.BaseCustomBot import BaseCustomBot
from haasomeapi.dataobjects.custombots.MadHatterBot import MadHatterBot
from haasomeapi.dataobjects.marketdata.Market import Market
from haasomeapi.dataobjects.util.HaasomeClientResponse import HaasomeClientResponse
from haasomeapi.enums.EnumCurrencyType import EnumCurrencyType
from haasomeapi.enums.EnumCustomBotType import EnumCustomBotType
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from haasomeapi.enums.EnumFundPosition import EnumFundPosition
from haasomeapi.enums.EnumMadHatterIndicators import EnumMadHatterIndicators
from haasomeapi.enums.EnumMadHatterSafeties import EnumMadHatterSafeties
from haasomeapi.enums.EnumOrderType import EnumOrderType
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
from haasomeapi.HaasomeClient import HaasomeClient
import init
import _thread
import botsellector
import configserver

# import expiration
import interval as iiv
from botdatabase import BotDB as bdb

haasomeClient = init.connect()


def bt_mh(current_bot):

    ticks = iiv.total_ticks(current_bot)
    bt = haasomeClient.customBotApi.backtest_custom_bot_on_market(
        current_bot.accountId,
        current_bot.guid,
        int(ticks),
        current_bot.priceMarket.primaryCurrency,
        current_bot.priceMarket.secondaryCurrency,
        current_bot.priceMarket.contractName,
    )
    if bt.errorCode != EnumErrorCode.SUCCESS:
        print("bt", bt.errorCode, bt.errorMessage)
    else:
        print(bt.result.roi)
    return bt.result


def setup_mad_hatter_bot(bot,config,haasomeClient):
        print(f'\n{bot.guid}')
        setup_bot = haasomeClient.customBotApi.setup_mad_hatter_bot(
            botName=bot.name,
            botGuid=bot.guid,
            accountGuid=bot.accountId,
            primaryCoin=bot.priceMarket.primaryCurrency,
            secondaryCoin=bot.priceMarket.secondaryCurrency,
            contractName=bot.priceMarket.contractName,
            leverage=bot.leverage,
            templateGuid=bot.customTemplate,
            position=bot.coinPosition,
            fee=bot.currentFeePercentage,
            tradeAmountType=bot.amountType,
            tradeAmount=bot.currentTradeAmount,
            useconsensus=config.useTwoSignals,
            disableAfterStopLoss=config.disableAfterStopLoss,
            interval=config.interval,
            includeIncompleteInterval=config.includeIncompleteInterval,
            mappedBuySignal=config.mappedBuySignal,
            mappedSellSignal=config.mappedSellSignal,
        )
        print(setup_bot.errorCode, setup_bot.errorMessage)



        # print(setup_bot.result.name, " Has been configured")
        return setup_bot.result


def err(variable):

    try:

        if variable.result != None:
            print(variable, variable.errorCode, variable.errorMessage)
        else:
            pass
    except AttributeError:
        pass


def clone_bot(bot, haasomeClient):

    botname = (
        str(bot.priceMarket.primaryCurrency)
        + str(" / ")
        + str(bot.priceMarket.secondaryCurrency)
        + str(" Roi ")
        + str(bot.roi)
    )
    cloned_bot = haasomeClient.customBotApi.clone_custom_bot(
        bot.accountId, bot.guid, bot.botType, bot.name, bot.priceMarket.secondaryCurrency,bot.priceMarket.secondaryCurrency,bot.priceMarket.contractName,bot.leverage
    ).result

    # err(mh_bot)

    print(f"Cloning {bot.name}...")
    return cloned_bot

    # curremt_bot =  setup_mad_hatter_bot(current_bot,haasomeClient)


def set_mh_params(selected_bot, config_bot, haasomeClient):


    if config_bot.botType == 15:
        # print(selected_bot.__dict__)
        if selected_bot.bBands["Length"] != config_bot.bBands["Length"]:
            do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                selected_bot.guid,
                EnumMadHatterIndicators.BBANDS,
                0,
                config_bot.bBands["Length"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    # pass
                    print(do.erro/rCode, do.errorMessage, 'Length')
            except:
                pass
        if selected_bot.bBands["Devup"] != config_bot.bBands["Devup"]:
            do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                selected_bot.guid,
                EnumMadHatterIndicators.BBANDS,
                1,
                config_bot.bBands["Devup"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    # pass
                    print(do.errorCode, do.errorMessage, 'Devup')
            except:
                pass
        if selected_bot.bBands["Devdn"] != config_bot.bBands["Devdn"]:
            do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                selected_bot.guid,
                EnumMadHatterIndicators.BBANDS,
                2,
                config_bot.bBands["Devdn"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                        pass
                        print(do.errorCode, do.errorMessage, 'Devdn')
            except:
                pass
        if selected_bot.bBands["MaType"] != config_bot.bBands["MaType"]:
            do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                selected_bot.guid,
                EnumMadHatterIndicators.BBANDS,
                3,
                config_bot.bBands["MaType"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    # pass
                    print(do.errorCode, do.errorMessage, 'MaType')
            except:
                pass
        if selected_bot.bBands["AllowMidSell"] != config_bot.bBands["AllowMidSell"]:
            do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                selected_bot.guid,
                EnumMadHatterIndicators.BBANDS,
                5,
                config_bot.bBands["AllowMidSell"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    # pass
                    print(do.errorCode, do.errorMessage, 'AllowMidSell')
            except:
                pass
        if selected_bot.bBands["RequireFcc"] != config_bot.bBands["RequireFcc"]:
            do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                selected_bot.guid,
                EnumMadHatterIndicators.BBANDS,
                6,
                config_bot.bBands["RequireFcc"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    # pass
                    print(do.errorCode, do.errorMessage, 'RequireFcc')
            except:
                pass
        if selected_bot.rsi["RsiLength"] != config_bot.rsi["RsiLength"]:
            do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                selected_bot.guid,
                EnumMadHatterIndicators.RSI,
                0,
                config_bot.rsi["RsiLength"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    # pass
                    print(do.errorCode, do.errorMessage, 'RsiLength')
            except:
                pass
        if selected_bot.rsi["RsiOverbought"] != config_bot.rsi["RsiOverbought"]:
            do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                selected_bot.guid,
                EnumMadHatterIndicators.RSI,
                1,
                config_bot.rsi["RsiOverbought"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    # pass
                    print(do.errorCode, do.errorMessage, 'RsiOverbought')
            except:
                pass
        if selected_bot.rsi["RsiOversold"] != config_bot.rsi["RsiOversold"]:
            do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                selected_bot.guid,
                EnumMadHatterIndicators.RSI,
                2,
                config_bot.rsi["RsiOversold"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    # pass
                    print(do.errorCode, do.errorMessage, 'RsiOversold')
            except:
                pass
        if selected_bot.macd["MacdFast"] != config_bot.macd["MacdFast"]:
            do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                selected_bot.guid,
                EnumMadHatterIndicators.MACD,
                0,
                config_bot.macd["MacdFast"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    # pass
                  print(do.errorCode, do.errorMessage, 'MacdFast')
            except:
                pass
        if selected_bot.macd["MacdSlow"] != config_bot.macd["MacdSlow"]:
            do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                selected_bot.guid,
                EnumMadHatterIndicators.MACD,
                1,
                config_bot.macd["MacdSlow"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    # pass
                    print(do.errorCode, do.errorMessage, 'MacdSlow')
            except:
                pass

        if selected_bot.macd["MacdSign"] != config_bot.macd["MacdSign"]:
            do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                selected_bot.guid,
                EnumMadHatterIndicators.MACD,
                2,
                config_bot.macd["MacdSign"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    # pass
                    print(do.errorCode, do.errorMessage, 'MacdSign')
            except:
                pass

        else:

            print(selected_bot.name, "indicators have been configured")
            return selected_bot
        return do.result
    else:
            return selected_bot


# def backtest_bot_configs(bot, configs, haasomeClient):

#     results = []
#     bot2 = clone_bot(bot, haasomeClient)
#     for config in configs:
#         param_bot = set_mh_params(bot2, config, haasomeClient)
#         set_safeties(bot2, config)

#         setup_mad_hatter_bot(bot, bot2, haasomeClient)
#         result3 = bt_mh(bot2)
#         results.append(bot2)

#     results = sorted(results, key=lambda x: x.roi, reverse=True)

#     delete_temp_bot(bot)
#     return results


def backtest_bot_configs(bot, configs, haasomeClient):

    results = []
    for config in configs:
        param_bot = set_mh_params(bot, config, haasomeClient)
        set_safeties(bot, config)

        setup_mad_hatter_bot(bot, config, haasomeClient)
        bt = bt_mh(bot)
        results.append(bt)

    results = sorted(results, key=lambda x: x.roi, reverse=True)

    return results


def delete_temp_bot(bot):

    delete = haasomeClient.customBotApi.remove_custom_bot(bot.guid)
    print(delete.errorCode, delete.errorMessage)


def bruteforce_mh(bot, haasomeClient):

    bt = bt_mh(bot)
    i = 0

    bot_config = [
        {
            "pricesource": EnumPriceSource(bot.priceMarket.priceSource).name,
            "primarycoin": bot.priceMarket.primaryCurrency,
            "secondarycoin": bot.priceMarket.secondaryCurrency,
            "interval": bot.interval,
            "signalconsensus": bot.useTwoSignals,
            "resetmiddle": bot.bBands["ResetMid"],
            "allowmidsells": bot.bBands["AllowMidSell"],
            "matype": bot.bBands["MaType"],
            "fcc": bot.bBands["RequireFcc"],
            "rsil": bot.rsi["RsiLength"],
            "rsib": bot.rsi["RsiOversold"],
            "rsis": bot.rsi["RsiOverbought"],
            "bbl": bot.bBands["Length"],
            "devup": bot.bBands["Devup"],
            "devdn": bot.bBands["Devdn"],
            "macdfast": bot.macd["MacdFast"],
            "macdslow": bot.macd["MacdSlow"],
            "macdsign": bot.macd["MacdSign"],
            "roi": bt.roi,
        }
    ]

    bot_config_pd = pd.DataFrame(bot_config, columns=bot_config[0].keys(),)

    return bot_config_pd


def bruteforce_rsi(bot, bot_config_pd, haasomeClient):

    btr = []
    btr.append(bot)

    rsil = int(bot.rsi["RsiLength"])
    rsis = int(bot.rsi["RsiOversold"])
    rsib = int(bot.rsi["RsiOverbought"])

    print(rsil, rsib, rsis)
    for l in range(rsil, rsil + 10):
        do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
            bot.guid, EnumMadHatterIndicators.RSI, 0, l
        )
        do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
            bot.guid, EnumMadHatterIndicators.RSI, 2, 80
        )
        do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
            bot.guid, EnumMadHatterIndicators.RSI, 1, 20
        )
        print(do.errorCode, do.errorMessage, "RsiLength")
        for x in range(rsis, rsis + 20, 3):
            do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid, EnumMadHatterIndicators.RSI, 1, x
            )
            print(do.errorCode, do.errorMessage, "RsiOverbought")

            for y in range(rsib, rsib - 20, -2):
                if y > 90:
                    pass
                else:
                    do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                        bot.guid, EnumMadHatterIndicators.RSI, 2, y
                    )
                    print(do.errorCode, do.errorMessage, "RsiOversold")

                    bt = bt_mh(bot)
                    bot_config = {
                        "pricesource": EnumPriceSource(bt.priceMarket.priceSource).name,
                        "primarycoin": bt.priceMarket.primaryCurrency,
                        "secondarycoin": bt.priceMarket.secondaryCurrency,
                        "interval": bt.interval,
                        "signalconsensus": bt.useTwoSignals,
                        "resetmiddle": bt.bBands["ResetMid"],
                        "allowmidsells": bt.bBands["AllowMidSell"],
                        "matype": bt.bBands["MaType"],
                        "fcc": bt.bBands["RequireFcc"],
                        "rsil": bt.rsi["RsiLength"],
                        "rsib": bt.rsi["RsiOversold"],
                        "rsis": bt.rsi["RsiOverbought"],
                        "bbl": bt.bBands["Length"],
                        "devup": bt.bBands["Devup"],
                        "devdn": bt.bBands["Devdn"],
                        "macdfast": bt.macd["MacdFast"],
                        "macdslow": bt.macd["MacdSlow"],
                        "macdsign": bt.macd["MacdSign"],
                        "roi": bt.roi,
                    }
                    bot_config_pd2 = pd.DataFrame([bot_config])
                    btr.append(bt)
                    # try:
                    # 	if btr[-1].roi > btr[-2].roi:

                    # bot_config_pd = pd.merge(bot_config_pd2, bot_config_pd)
                    # bot_config_pd.append(bot_config_pd2, ignore_index=True)
                    print(bot_config_pd2)
    # print(bot_config_pd)
    # for bot in btr:
    # 	print(bot.guid)
    sorti = sorted(btr, key=lambda x: x.roi, reverse=True)
    for i in sorti:
        print(i.roi)
    do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
        bot.guid, EnumMadHatterIndicators.RSI, 0, sorti[1].rsi["RsiLength"]
    )
    print(
        do.errorCode,
        do.errorMessage,
        sorti[1].rsi["RsiLength"],
        sorti[1].rsi["RsiOversold"],
        sorti[1].rsi["RsiOverbought"],
    )
    do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
        bot.guid, EnumMadHatterIndicators.RSI, 1, sorti[1].rsi["RsiOversold"]
    )
    do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
        bot.guid, EnumMadHatterIndicators.RSI, 2, sorti[1].rsi["RsiOverbought"]
    )
    print("hey hey", bot.guid, btr[0].guid)

    BotDB.save_configs_for_same_bot_to_file(btr)
    return bot_config_pd


def find_good_safety(bot, haasomeClient):

    print(bot.name, "is selected")
    best_roi = bot.roi
    print(best_roi)
    ticks = int(iiv.readinterval(bot))
    stoploss = []
    same_roi = 0
    if bot.platformType == 0:
        for x in np.arange(0.9, 5.0, 0.1):
            if same_roi >= 1:
                same_roi = 0
                continue
            # try:
            # 	if stoploss[-1][0] == stoploss[-2][0] and stoploss[-2][0] == stoploss[-3][0] and stoploss[-3][0] == stoploss[-4][0] and stoploss[-4][0] == stoploss[-5][0]:
            # 		print('looks like we hit a limit on how far safety can be pushed')
            # 		continue
            # except:
            # 	pass
            stopLoss = haasomeClient.customBotApi.set_mad_hatter_safety_parameter(
                bot.guid, EnumMadHatterSafeties.STOP_LOSS, round(x, 2)
            )
            backtest = haasomeClient.customBotApi.backtest_custom_bot_on_market(
                bot.accountId,
                bot.guid,
                ticks,
                bot.priceMarket.primaryCurrency,
                bot.priceMarket.secondaryCurrency,
                bot.priceMarket.contractName,
            )
            backtestr = backtest.result
            roi = backtestr.roi
            print("With Stoploss", round(x, 2), "ROI is: ", roi)
            stoploss.append([roi, round(x, 2)])

            try:
                print(stoploss[-1], stoploss[-2], "same roi count: ", same_roi)
            except:
                pass
            try:
                if stoploss[-1][0] == stoploss[-2][0]:
                    same_roi += 1
            except:
                pass

    if bot.platformType == 2:
        for x in np.arange(0.0, 200.0, 10.0):
            stopLoss = haasomeClient.customBotApi.set_mad_hatter_safety_parameter(
                bot.guid, EnumMadHatterSafeties.STOP_LOSS, round(x, 2)
            )
            backtest = haasomeClient.customBotApi.backtest_custom_bot_on_market(
                bot.accountId,
                bot.guid,
                ticks,
                bot.priceMarket.primaryCurrency,
                bot.priceMarket.secondaryCurrency,
                bot.priceMarket.contractName,
            )
            backtestr = backtest.result
            roi = backtestr.roi
            print("With Stoploss", x, "ROI is: ", roi)
            stoploss.append([roi, round(x, 2)])

    sortedstoploss = sorted(stoploss, key=lambda x: x[0], reverse=True)
    if sortedstoploss[0][1] >= best_roi:
        stopLoss = haasomeClient.customBotApi.set_mad_hatter_safety_parameter(
            bot.guid, EnumMadHatterSafeties.STOP_LOSS, sortedstoploss[0][1]
        )
        print(
            "Stoploss has been set to ",
            sortedstoploss[0][1],
            "with ROI: ",
            sortedstoploss[0][0],
        )
    else:
        stopLoss = haasomeClient.customBotApi.set_mad_hatter_safety_parameter(
            bot.guid, EnumMadHatterSafeties.STOP_LOSS, 0
        )


def makebots(bot, haasomeClient, botType, botlist):

        # print(botlist[1], botlist[0])
    for i, b in enumerate(botlist):
        print(f"{i}:{b.roi},{len(b.completedOrders)} trades")
    x = int(input("Type bot number to setup given ROI config on a currently selected mad-hatter bot. Once satisfied, hit return without entering bot number and the app will initiate automatic stoploss backtesting. Enter bot number here: "))

    ticks = int(iiv.readinterval(bot))
    setup_bot = setup_mad_hatter_bot(bot, botlist[x], haasomeClient)
    setup_bot = set_mh_params(bot, botlist[x], haasomeClient)
    clone = clone_bot(setup_bot,haasomeClient)


    return setup_bot


def autocreate_bots(bot, haasomeClient, botType, botlist, x):

    bl = []
    ticks = int(iiv.readinterval(bot))
    for y in range(x):
        try:
            bot0 = clone_bot(bot, haasomeClient)
            bot2 = set_mh_params(bot2, botlist[int(y)], haasomeClient)
            bot3 = set_safeties(botlist[int(y)], bot2)
            bt = haasomeClient.customBotApi.backtest_custom_bot(
                bot2.guid, ticks)
            bl.append(bt.result)
        except IndexError:
            pass
            return None
        return bl


def load_bots_from_file(BotDB):
     db_file = BotDB.get_haasbots_file()
     print(f'{db_file} db_file')
     # print(botlistfile)
     configs = BotDB.load_botlist(db_file)
     return configs

def set_safeties(bot, config_bot):

    sellStep = haasomeClient.customBotApi.set_mad_hatter_safety_parameter(
        bot.guid,
        EnumMadHatterSafeties.PRICE_CHANGE_TO_SELL,
        config_bot.priceChangeToSell,
    )
    err(sellStep)
    buyStep = haasomeClient.customBotApi.set_mad_hatter_safety_parameter(
        bot.guid, EnumMadHatterSafeties.PRICE_CHANGE_TO_BUY, config_bot.priceChangeToBuy
    )
    err(buyStep)
    stopLoss = haasomeClient.customBotApi.set_mad_hatter_safety_parameter(
        bot.guid, EnumMadHatterSafeties.STOP_LOSS, config_bot.stopLoss
    )
    err(stopLoss)


def intro():

    bt = configserver.read_bt()
    BotDB = bdb()
    print("1. Backtest a bot with set of configs from a file")
    print("2. Change BT period.")
    # print('3. Analyze and create bots stored in files, be it saved bt results or of another machine')
    print("4. bruteforce bot params ")
    print("5. Backtest single Mad Hatter Safety")
    print("6. Backtest every bot with name starting with word Tune")
    print(f'7. Carousel between configs.')
    # response = input('Type number of action here: ')
    while True:
        response = input("Type number of action here: ")
        while True:
            if response == "1":
                # results = []
                bot = botsellector.get_mh_bot(haasomeClient)
                # db_file = BotDB.get_haasbots_file()
                # print(f'{db_file} db_file')
                # # print(botlistfile)
                # configs = BotDB.load_botlist(db_file)
                configs = BotDB.get_configs_from_file()

                print(
                    "\n\nMost files contain a limited number of configs, indicating they were created at the end of backtesting stage and thus are sorted in a descending manner, with top-performing configs at the top.\n You have an option to only use specified number of configurations from a file."
                )
                print("\nCurrent file contains ",
                      len(configs), "bot configs\n")
                limit = int(input("Type number of configs to use: "))
                results = backtest_bot_configs(
                    bot, configs[0:limit], haasomeClient)
                created = []
                # BotDB.save_configs_for_same_bot_to_file(results)
                while True:
                    try:
                        new = makebots(bot, haasomeClient,
                                       bot.botType, results)
                        created.append(new)
                    except ValueError:
                        break

                for bot in created:
                    find_good_safety(bot, haasomeClient)
                break

            elif response == "2":

                configserver.set_bt()

                break

            elif response == "3":
                botlistfile = BotDB.get_botlist_file()
                bots = BotDB.load_bots_from_file(botlistfile)
                history.plot_bots(bots)

            elif response == "4":
                bot = botsellector.get_mh_bot(haasomeClient)
                # safety = find_good_safety(bot,haasomeClient)
                brute = bruteforce_mh(bot, haasomeClient)
                bruteforce_rsi(bot, brute, haasomeClient)
                break
            elif response == "5":
                bot = botsellector.get_mh_bot(haasomeClient)
                find_good_safety(bot, haasomeClient)
            elif response == "6":
                botlist = botsellector.gets_pecific_mh_bot_list(haasomeClient)
                botlistfile = BotDB.get_botlist_file()
                configs = BotDB.load_bots_from_file(botlistfile)
                print(
                    "\n\nMost files contain a limited number of configs, indicating they were created at the end of backtesting stage and thus are sorted in a descending manner, with top-performing configs at the top.\n You have an option to only use specified number of configurations from a file."
                )
                print("\nCurrent file contains ",
                      len(configs), "bot configs\n")
                limit = int(input("Type number of configs to use: "))
                x = int(
                    input(
                        "After backtesting is complete, there will be multiple results for each. In this mode you need to input a number of bots to be created auutomatically for now. Enter it now: "
                    )
                )
                for bot in botlist:
                    results = backtest_bot_configs(
                        bot, configs[0:limit], haasomeClient)
                    BotDB.save_configs_for_same_bot_to_file(results)
                    bl = autocreate_bots(bot, haasomeClient,
                                         bot.botType, results, x)
                    for b in bl:
                        find_good_safety(b, haasomeClient)
                    break
            elif response == "7":

                configserver.set_bt()

                break
            else:
                pass
        break
    #  1/11/19 16:30


def main():

    configserver.set_bt()
    bot = botsellector.get_mh_bot(haasomeClient)
    botlistfile = BotDB.get_botlist_file()
    configs = BotDB.load_bots_from_file(botlistfile)
    # print(configs[:10])
    results = bt_bot_configs(bot, configs, haasomeClient)


if __name__ == "__main__":
    intro()
