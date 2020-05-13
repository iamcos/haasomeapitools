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


'''
BotDB class contains a variable self.c and in it, cnt function returns our api client object which can be used to interact with Bot, Market and Trades data, to place and cancel orders, to clone bots, setup custombots and trade bots: setup/add/remove indicators/safeties/insurances with trade bots.
Backtesting can also be done through api.
'''

### Mad Hatter Bot
'''
In this tutorial we will concentrate only on Mad-Hatter Bot interactions. With HaasomeAPI its possible to load csv file full of mad-hatter cofiguration files and iterate over them, logging backtesting results. in order to load csv we will use pandas. So lets import it
'''


class BotDB(BotDB):
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
            if bot.bBands["Length"] != config['bbl']: #if params differ - applies new one.
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter( #this way less api calls is being made
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                0,
                    config['bbl']
            )

            if bot.bBands["Devup"] != config['devup']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.BBANDS,
                    1,
                    config['devup'],
                )


            if bot.bBands["Devdn"] != config['devdn']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                2,
                config['devdn'],
                )


            if bot.bBands["MaType"] != config['matype']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                3,
                config['matype'],
                )


            if bot.bBands["AllowMidSell"] != config['allowmidsells']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                5,
                config['allowmidsells'],
                )


            if bot.bBands["RequireFcc"] != config['fcc']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                6,
                config['fcc'],
                )


            if bot.rsi["RsiLength"] != config['rsil']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.RSI,
                0,
                config['rsil'],
                )


            if bot.rsi["RsiOverbought"] != config['rsib']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.RSI,
                1,
                config['rsib'],
                )


            if bot.rsi["RsiOversold"] != config['rsis']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.RSI,
                2,
                config['rsis'],           )


            if bot.macd["MacdFast"] != config['macdfast']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.MACD,
                0,
                config['macdfast'],
                )

            if bot.macd["MacdSlow"] != config['macdslow']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.MACD,
                1,
                config['macdslow'],
                )


            if bot.macd["MacdSign"] != config['macdsign']:
                do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.MACD,
                2,
                config['macdsign'],
                )

                                                                        #Indicator parameters have been set


            if bot.interval != config['interval']:
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
                interval=config['interval'],
                includeIncompleteInterval=bot.includeIncompleteInterval,
                mappedBuySignal=bot.mappedBuySignal,
                mappedSellSignal=bot.mappedSellSignal,).result


            print(bot.name,' Has been configured')

                                                                # And here we set bot's safeties.
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
    def bt_bot(self,bot):
        bt = self.c.customBotApi.backtest_custom_bot_on_market(
                    bot.accountId,
                    bot.guid,
                    int(depth),
                    bot.priceMarket.primaryCurrency,
                    bot.priceMarket.secondaryCurrency,
                    bot.priceMarket.contractName)
        #     print(bt.errorCode)
        print(bt.result.roi)
        return bt

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
            diff = {}
            for i in ['rsi', 'bBands', 'macd', 'interval']:
                diff[i] = bot[i].items() ^ bot1[i].items()
            print(diff)