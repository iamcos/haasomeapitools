import configserver
from functools import lru_cache
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from haasomeapi.HaasomeClient import HaasomeClient
import configserver
from haasomeapi.HaasomeClient import HaasomeClient
import os
from ratelimit import limits, sleep_and_retry
import pandas as pd
from haasomeapi.enums.EnumMadHatterIndicators import EnumMadHatterIndicators
from haasomeapi.enums.EnumMadHatterSafeties import EnumMadHatterSafeties
import datetime
from botsellector import BotSellector
from BaseHaas import Bot, Haas

class BotDB:
    def __init__(self):
        self.c = self.cnt()

    def cnt(self):
        ip, secret = Haas().read_config()
        haasomeClient = HaasomeClient(ip, secret)
        return haasomeClient

    def csv_to_sellectionbox(self):
        files = self.get_csv_files()

        return files

    def get_csv_files(self):
        files = []
        for file in os.listdir('./'):
            if file.endswith(".csv") or file.endswith('.json'):
                files.append(os.path.join('./', file))
        return files
    def select_from_list(self, files):
        for i, file in enumerate(files):
            print(i, file)
        userinput = input('Type file number to select it:  ')
        self.db_file = files[int(userinput)]
        return files[int(userinput)]

    def read_csv(self, file):
        # This is how we turn CSV file from previous step into a DataFrame.
        if file.endswith('.csv'):
            try:
                configs = pd.read_csv(file)
                # print(configs[0])
            except Exception as e:
                print('csv',e)
        elif file.endswith('.json'):

            try:
                configs=pd.read_json(file)
                # print(configs[0])
            except Exception as e:
                print('json',e)
            # configs.head()  # prints Dataframe Head
        return configs


    def get_mh_bots(self):
        all_bots = BotSellector().get_all_custom_bots()  # getting all bots here
        # sorting them to only Mad Hatter Bot(bot type 15 )
        all_mh_bots = [x for x in all_bots if x.botType == 15]
        opts = [[x.name, x] for x in all_mh_bots]  # making botlist with names
        return opts

    def setup_bot_from_csv(self, bot, config):

        # if params differ - applies new one.
        if bot.bBands["Length"] != config['bbl']:
            do = self.c.customBotApi.set_mad_hatter_indicator_parameter(  # this way less api calls is being made
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
                config['rsis'],)

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

    # calling it setup_bot_from_obj. It checks each parameter against new config.
    def setup_bot_from_obj(self, bot, config):


        if bot.bBands["Length"] != config.bBands['Length']:
            do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
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
                config.rsi['RsiOversold'],)

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
        if bot.interval != config.interval:
            setup_bot_from_obj = self.c.customBotApi.setup_mad_hatter_bot(  # This code sets time interval as main goalj
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
                useconsensus=bot.useTwoSignals,
                disableAfterStopLoss=bot.disableAfterStopLoss,
                interval=config.interval,
                includeIncompleteInterval=bot.includeIncompleteInterval,
                mappedBuySignal=bot.mappedBuySignal,
                mappedSellSignal=bot.mappedSellSignal,).result

        print(bot.name, ' Has been configured')
            #Indicator parameters have been set

        if bot.interval != config.interval:
            setup_bot_from_obj = self.c.customBotApi.setup_mad_hatter_bot(  # This code sets time interval as main goalj
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
                useconsensus=bot.useTwoSignals,
                disableAfterStopLoss=bot.disableAfterStopLoss,
                interval=config.interval,
                includeIncompleteInterval=bot.includeIncompleteInterval,
                mappedBuySignal=bot.mappedBuySignal,
                mappedSellSignal=bot.mappedSellSignal,).result

        print(bot.name, ' Has been configured')

    # @lru_cache(maxsize=None)
    def bt_bot(self, bot, depth):
        bt = self.c.customBotApi.backtest_custom_bot(

            bot.guid,
            depth)

        # print(btres.roi)
        return bt.result

    def iterate_csv(self, configs, bot, depth):
        for i in configs.index:
            config = configs.iloc[i]
            self.setup_bot_from_csv(bot, config)
#             print(config)
            bt = self.c.customBotApi.backtest_custom_bot_on_market(
                bot.accountId,
                bot.guid,
                int(depth),
                bot.priceMarket.primaryCurrency,
                bot.priceMarket.secondaryCurrencyn,
                bot.priceMarket.contractName).result
            # bt = self.bt_bot(bot,depth)
            configs['roi'][i] = bt.roi
            print(bt.roi)
#             configs['botobject'] = bt.result
        return configs

    def verify_cfg(self):
        c = ConfigParser


if __name__ == "__main__":
    pass