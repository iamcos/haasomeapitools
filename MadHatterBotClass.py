
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

    def configure_mh_from_another_bot(self, config, bot_to_setup):

        setup_bot = self.c().customBotApi.setup_mad_hatter_bot(
        botName = config.name,
        botGuid=bot_to_setup.guid,
        accountGuid=config.accountId,
        primaryCoin=config.priceMarket.primaryCurrency,
        secondaryCoin=config.priceMarket.secondaryCurrency,
        contractName=config.priceMarket.contractName,
        leverage=config.leverage,
        templateGuid=config.customTemplate,
        position=config.coinPosition,
        fee=config.currentFeePercentage,
        tradeAmountType=config.amountType,
        tradeAmount=config.currentTradeAmount,
        useconsensus=config.useTwoSignals,
        disableAfterStopLoss=config.disableAfterStopLoss,
        interval=config.interval,
        includeIncompleteInterval=config.includeIncompleteInterval,
        mappedBuySignal=config.mappedBuySignal,
        mappedSellSignal=config.mappedSellSignal,).result

        # print(setup_bot,' Has been configured')
        return setup_bot

    def clone_bot_for_bt(self, bot,name):
        clones = []

        clone = self.c().customBotApi.clone_custom_bot(bot.accountId, bot.guid, EnumCustomBotType.MAD_HATTER_BOT, bot.name, bot.priceMarket.primaryCurrency, bot.priceMarket.secondaryCurrency, bot.priceMarket.contractName, bot.leverage).result

        return clone
    def delete_temp_bot(self, bot):
        self.c().customBotApi.remove_custom_bot(bot.guid)

    def clone_bot_for_bt2(self, bot,name):
            clone = self.c().customBotApi.clone_custom_bot_simple(bot.accountId, bot.guid, bot.name).result
            return clone
    def return_bot(self, guid):
        bot = self.c().customBotApi.get_custom_bot(
            guid, EnumCustomBotType.MAD_HATTER_BOT)


        # print(bot.errorCode, bot.errorMessage)
        # print(bot.result.__dict__)
        return bot.result
    def return_botlist(self):
        bl = self.c().customBotApi.get_all_custom_bots().result
        botlist = [x for x in bl if x.botType == 15]
        # print(botlist)
        return botlist

    def set_safety_parameters(self,bot, config):
        sellStep = self.c().customBotApi.set_mad_hatter_safety_parameter(
            bot.guid, EnumMadHatterSafeties.PRICE_CHANGE_TO_SELL, config.priceChangeToSell)
        # print('Safety parameter ',' sellStep',' has been setup')
        buyStep = self.c().customBotApi.set_mad_hatter_safety_parameter(
            bot.guid, EnumMadHatterSafeties.PRICE_CHANGE_TO_BUY, config.priceChangeToBuy)
        # print('Safety parameter ','buyStep',' has been setup')
        stopLoss = self.c().customBotApi.set_mad_hatter_safety_parameter(
            bot.guid, EnumMadHatterSafeties.STOP_LOSS, config.stopLoss)
        # print('Safety parameter ','stopLoss',' has been setup')

        # print(stopLoss.errorCode, stopLoss.errorMessage)
        # print(sellStep.errorCode, sellStep.errorMessage)
        # print(buyStep.errorCode,buyStep.errorMessage)

    def setup(self, bot,configs, index = None):

        if index == None:

                result,botconfig = self.apply_config_to_madhatter_bot(bot, configs, 0)
                return result,botconfig
        else:
                result = self.apply_config_to_madhatter_bot(bot,configs,str(index))
                return result.sort_values(by='roi', ascending=False)



    def apply_config_to_madhatter_bot(self, bot, bot_configs, ind):
        configs = bot_configs.iloc[ind]

        if bot.bBands["Length"] != configs['bbl']:
            do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
            bot.guid,
            EnumMadHatterIndicators.BBANDS,
            0,
                configs['bbl']
        )
        if bot.bBands["Devup"] != configs['devup']:
            do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                1,
                configs['devup'],
            )
        if bot.bBands["Devdn"] != configs['devdn']:
            do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                2,
                configs['devdn'],
            )
        if bot.bBands["MaType"] != configs['matype']:
            do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                3,
                configs['matype'],
            )
        if bot.bBands["AllowMidSell"] != configs['allowmidsells']:
            do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                5,
                configs['allowmidsells'],
            )
        if bot.bBands["RequireFcc"] != configs['fcc']:
            do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                6,
                configs['fcc'],
            )
        if bot.rsi["RsiLength"] != configs['rsil']:
            do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.RSI,
                0,
                configs['rsil'],
            )
        if bot.rsi["RsiOverbought"] != configs['rsib']:
            do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.RSI,
                1,
                configs['rsib'],
            )
        if bot.rsi["RsiOversold"] != configs['rsis']:
            do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.RSI,
                2,
                configs['rsis'],
            )
        if bot.macd["MacdFast"] != configs['macdfast']:
            do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.MACD,
                0,
                configs['macdfast'],
            )
        if bot.macd["MacdSlow"] != configs['macdslow']:
            do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.MACD,
                1,
                configs['macdslow'],
            )
        if bot.macd["MacdSign"] != configs['macdsign']:
            do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.MACD,
                2,
                configs['macdsign'],
            )
        if bot.interval != configs['interval']:
            botname = str(bot.priceMarket.primaryCurrency) + str(' / ') + \
                str(bot.priceMarket.secondaryCurrency) + str(' Roi ') + str(bot.roi)
            setup_bot = self.c().customBotApi.setup_mad_hatter_bot(
            botName = bot.name,
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
            useconsensus=bot.useTwoSignals,
            disableAfterStopLoss=bot.disableAfterStopLoss,
            interval=configs['interval'],
            includeIncompleteInterval=bot.includeIncompleteInterval,
            mappedBuySignal=bot.mappedBuySignal,
            mappedSellSignal=bot.mappedSellSignal,).result
            # print(bot.name,' Has been configured')

        else:
            print(bot.name,' Has been configured')
        return bot_configs


    def bt_mh(self,bot):

        ticks = iiv.total_ticks()
        bt = self.c().customBotApi.backtest_custom_bot_on_market(
            bot.accountId,
            bot.guid,
            int(ticks),
            bot.priceMarket.primaryCurrency,
            bot.priceMarket.secondaryCurrency,
            bot.priceMarket.contractName,
        )
        if bt.errorCode != EnumErrorCode.SUCCESS:
            print("bt", bt.errorCode, bt.errorMessage)
        else:
            # print(bt.result.roi)
            return bt.result

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

    def bt_bot_configs(self, bot):
        configs = BotDB().csv_to_dataframe()
        results = self.setup(bot, configs )
        BotDB().dataframe_to_csv(bot, results)
        results = sorted(results, key=lambda x: x.roi, reverse=True)
        return results

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


        df = pd.DataFrame(botdict)
        # print(df.loc['orderbook'])
        # d = df.orderbook
        # print('d',[k,y for k y in d.items()])
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
                            bot = self.bt_mh_on_update(x[1],ticks)
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
1
