
from BaseHaas import Bot
from haasomeapi.enums.EnumCustomBotType import EnumCustomBotType
import json
import os
import pickle
import csv
import interval as iiv
import jsonpickle
import datetime
from datetime import datetime
from pathlib import Path
from ratelimit import limits, sleep_and_retry
from numpy import arange
import base64, zlib, gzip
import pandas as pd
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from random import random
import time
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
from haasomeapi.HaasomeClient import HaasomeClient
from haasomeapi.enums.EnumMadHatterSafeties import EnumMadHatterSafeties
from haasomeapi.enums.EnumMadHatterIndicators import EnumMadHatterIndicators
from botsellector import BotSellector
from botdatabase import BotDB
from functools import lru_cache
from time import sleep
import timeit

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
                        +str(" / ")
                        +str(config.priceMarket.secondaryCurrency)
                        +str(" Roi ")
                        +str(config.roi))
        new_bot = self.create_mh(example_bot, botname)
        self.configure_mh_from_another_bot(config, new_bot)
        return new_bot.result

    def bruteforce_indicators(self, bot):

            d = self.bruteforce_rsi_corridor(bot)

    def bot_config(self,bot):
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
                    'orderbook': [{x:y for x,y in self.trades_to_df(bot).items()}]}


        return df



    def bruteforce_rsi_corridor(self,bot):
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

            config,botobj = self.setup(bot, botconfig)
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
        ranges['macdslow'] = list(range(40,80,2))
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
            completedOrders = [{'orderId': None,'orderStatus':None, 'orderType':None, 'price': None,'amount':None,'amountFilled':None,'unixTimeStamp':datetime.today()}for x in range(1)]
            orders_df = pd.DataFrame(completedOrders)
        return orders_df
    # @sleep_and_retry
    # @limits(calls=3, period=2)
