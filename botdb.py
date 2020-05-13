import configserver
from functools import lru_cache
from haasomeapi.HaasomeClient import HaasomeClient
import configserver
from haasomeapi.HaasomeClient import HaasomeClient
import os
import pandas as pd
from haasomeapi.enums.EnumMadHatterIndicators import EnumMadHatterIndicators
from haasomeapi.enums.EnumMadHatterSafeties import EnumMadHatterSafeties
import datetime
from botsellector import BotSellector
class BotDB:
    def __init__(self):
        self.c = self.cnt()

    def cnt(self):
        ip, secret = configserver.validateserverdata()
        haasomeClient = HaasomeClient(ip, secret)
        return haasomeClient

    def csv_to_sellectionbox(self):
        files = self.get_csv_files()

        return files

    def get_csv_files(self):
        files =[]
        for file in os.listdir('./'):
            if file.endswith(".csv"):
                files.append(os.path.join('./', file))


        return files

    def select_from_list(self,files):
        for i, file in enumerate(files):
                    print(i, file)
        userinput = input('Type file number to select it:  ')
        self.db_file = files[int(userinput)]
        return files[int(userinput)]




    def get_mh_bots(self):
        all_bots = BotSellector().get_all_custom_bots() #getting all bots here
        all_mh_bots = [x for x in all_bots if x.botType == 15] #sorting them to only Mad Hatter Bot(bot type 15 )
        opts= [[x.name,x] for x in all_mh_bots] #making botlist with names
        return opts


    def setup_bot(self,bot,config): #calling it setup_bot. It checks each parameter against new config.
            if bot.bBands["Length"] != config.bBands['Length']: #if params differ - applies new one.
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter( #this way less api calls is being made
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                0,
                    config.bBands['Length']
            )

            if bot.bBands["Devup"] != config.bBands['Devup']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.BBANDS,
                    1,
                    config.bBands['Devup'],
                )


            if bot.bBands["Devdn"] != config.bBands['Devdn']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                2,
                config.bBands['Devdn'],
                )


            if bot.bBands["MaType"] != config.bBands['MaType']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                3,
                config.bBands['MaType'],
                )


            if bot.bBands["AllowMidSell"] != config.bBands['AllowMidSell']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                5,
                config.bBands['AllowMidSell'],
                )


            if bot.bBands["RequireFcc"] != config.bBands['RequireFcc']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                6,
                config.bBands['RequireFcc'],
                )


            if bot.rsi["RsiLength"] != config.rsi['RsiLength']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.RSI,
                0,
                config.rsi['RsiLength'],
                )


            if bot.rsi["RsiOverbought"] != config.rsi['RsiOverbought']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.RSI,
                1,
                config.rsi['RsiOverbought'],
                )


            if bot.rsi["RsiOversold"] != config.rsi['RsiOversold']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.RSI,
                2,
                config.rsi['RsiOversold'],           )


            if bot.macd["MacdFast"] != config.macd['MacdFast']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.MACD,
                0,
                config.macd['MacdFast'],
                )

            if bot.macd["MacdSlow"] != config.macd['MacdSlow']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.MACD,
                1,
                config.macd['MacdSlow'],
                )


            if bot.macd["MacdSign"] != config.macd['MacdSign']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.MACD,
                2,
                config.macd['MacdSign'],
                )

                                                                        #Indicator parameters have been set


            if bot.interval != config.interval:
                setup_bot = self.c.customBotApi.setup_mad_hatter_bot( # This code sets time interval as main goalj
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
                interval=config.interval,
                includeIncompleteInterval=bot.includeIncompleteInterval,
                mappedBuySignal=bot.mappedBuySignal,
                mappedSellSignal=bot.mappedSellSignal,).result


            print(bot.name,' Has been configured')

    def set_safety_parameters(newbot, example_bot):
        sellStep = self.c.customBotApi.set_mad_hatter_safety_parameter(
            newbot.guid, EnumMadHatterSafeties.PRICE_CHANGE_TO_SELL, example_bot.priceChangeToSell)
        print(sellStep.errorCode,sellStep.errorMessage)
        buyStep = self.c.customBotApi.set_mad_hatter_safety_parameter(
            newbot.guid, EnumMadHatterSafeties.PRICE_CHANGE_TO_BUY, example_bot.priceChangeToBuy)
        print(buyStep.errorCode,buyStep.errorMessage)
        stopLoss = self.c.customBotApi.set_mad_hatter_safety_parameter(
            newbot.guid, EnumMadHatterSafeties.STOP_LOSS, example_bot.stopLoss)
        print(stopLoss.errorCode,stopLoss.errorMessage)

    def calculate_ticks(start_date,end_date):
        diff = end_date-start_date
        secs = diff.total_seconds()/60
        return int(secs)
    @lru_cache(maxsize=None)
    def bt_bot(self,bot):
        bt = self.c.customBotApi.backtest_custom_bot(
  
                    bot.guid,
                    int(100))
 
        print(bt.result.roi)
        return bt.result

    def iterate(self,configs,bot):
        for i in configs.index:
            config = configs.iloc[i]
            self.setup_bot(bot,config)
            print(config)
            print(bot)
            bt = self.c.customBotApi.backtest_custom_bot_on_market(
                    bot.guid,
                    int(depth))
            configs['roi'] = bt.result.roi
            configs['botobject'] = bt.result
        return configs

    def compare_indicators(self, bot, bot1):
            # print(bot.rsi, '\n',bot1.rsi)
            
         
            rsi=set(bot.rsi.items()) ^ set(bot1.rsi.items())
            macd=set(bot.macd.items()) ^ set(bot1.macd.items())
            bBands=set(bot.bBands.items()) ^ set(bot1.bBands.items())
            print(rsi,bBands,macd)
        
             
            rsi=bot.rsi - bot1.rsi
            macd=bot.macd - bot1.macd
            bBands=bot.bBands - bot1.bBands
            print(rsi,bBands,macd)
        
    