
from botsellector import BotSellector
import configserver
import json
import os
from haasomeapi.enums.EnumCustomBotType import EnumCustomBotType
import pickle
import csv
import interval as iiv
import jsonpickle
import datetime
import pandas as pd
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
import time
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
from haasomeapi.HaasomeClient import HaasomeClient
from haasomeapi.enums.EnumMadHatterSafeties import EnumMadHatterSafeties
from haasomeapi.enums.EnumMadHatterIndicators import EnumMadHatterIndicators


class BotDB:
    def __init__(self):
        self.c = self.cnt()

    def cnt(self):
        ip, secret = configserver.validateserverdata()
        haasomeClient = HaasomeClient(ip, secret)
        return haasomeClient

    def get_all_markets(self):
        pass

    def return_priceMarket_object(self, df, pricesource, primarycoin, secondarycoin):
        '''
            Returns priceSource object for given pricesorce, primarycoin, secondarycoin if that pricesource is enabled in Haas.
        '''

        obj = df[df["pricesource"] == pricesource][df["primarycurrency"]
                                                   == primarycoin][df["secondarycurrency"] == secondarycoin].values
        print('obj', obj)
        return obj[0][3]

    def iterate_over_market_coinpairs(self):
        botlist = BotSellector().return_all_mh_bots(self.c)
        bot = BotSellector().get_mad_hatter_bot(self.c, botlist)
        configs = self.csv_to_dataframe()
        markets = self.get_all_markets()
        selected_market = ''
        pricesources = [x for x in markets.pricesource.unique()]
        for i, p in enumerate(pricesources):
            print(i, p)
        uip = input('Type market number in to use')

        market_pairs = markets[markets["pricesource"]
                               == pricesources[int(uip)]]
        print(market_pairs)
        coinpairs = []
        while True:
            uip = input('Type base coin')
        primarycurrency = [x for x in market_pairs.primarycurrency.unique()]
        secondarycurrency = [
            x for x in market_pairs.secondarycurrency.unique()]
        for c in primarycurrency:
            for cc in secondarycurrency:
                try:
                    print(pricesources[int(uip)], c, cc)
                    pmo = self.return_priceMarket_object(
                        markets, pricesources[int(uip)], c, cc)

                except:
                    pass
                change_coin = self.c.customBotApi.setup_mad_hatter_bot(
                    botName=bot.name,
                    botGuid=bot.guid,
                    accountGuid=bot.accountId,
                    primaryCoin=pmo.primaryCurrency,
                    secondaryCoin=pmo.secondaryCurrency,
                    contractName=pmo.contractName,
                    leverage=bot.leverage,
                    templateGuid=bot.customTemplate,
                    position=bot.coinPosition,
                    fee=bot.currentFeePercentage,
                    tradeAmountType=bot.amountType,
                    tradeAmount=bot.currentTradeAmount,
                    useconsensus=bot.useTwoSignals,
                    disableAfterStopLoss=bot.disableAfterStopLoss,
                    interval=bot.interval,
                    includeIncompleteInterval=bot.includeIncompleteInterval,
                    mappedBuySignal=bot.mappedBuySignal,
                    mappedSellSignal=bot.mappedSellSignal,)
            print(change_coin.errorCode, change.coin.errorMessage)

            print(bot.name, ' Has been configured to ', p,
                  c, cc, 'markets')
            results = self.setup(bot, configs)

            results.sort_values(by='roi', ascending=False, inplace=True)
            BotDB().dataframe_to_csv(bot, results)
            self.save_configs_for_same_bot_to_file(results.botobject)

    def get_csv_file(self):
        files = []
        for file in os.listdir('./'):
            if file.endswith(".csv"):
                files.append(os.path.join('./', file))
        for i, file in enumerate(files):
            print(i, file)
        userinput = input('Type file number to select it:  ')
        self.db_file = files[int(userinput)]
        return files[int(userinput)]

    def get_haasbots_file(self):
        # Returns bot-containing list of files from home folder
        files = []
        for file in os.listdir('./'):
            if file.endswith(".haasbots"):
                files.append(os.path.join('./', file))
        for i, file in enumerate(files):
            print(i, file)
        userinput = input('Type file number to select it:  ')
        self.db_file = files[int(userinput)]
        return files[int(userinput)]

    def load_bots_from_file(self, file):
        db_file = file
        print(f'{db_file} db_file')
        # print(botlistfile)
        configs = self.load_botlist(db_file)
        return configs

    def get_configs_from_file(self):
        file = self.get_haasbots_file()
        configs = self.load_bots_from_file(file)
        return configs

    def return_single_bot_files(self):
        # returns filepath to user specified file from the above list
        local_path = './'
        files = []
        for file in os.listdir(local_path):
            if file.endswith(".haasbot"):
                files.append(os.path.join(local_path, file))
        try:
            for i, file in enumerate(files):
                print(i, file)
        except FileNotFoundError:
            print('looks like there are no files that contain haasbots in them')
        userinput = input('Type file number to select it:  ')
        return files[int(userinput)]

    def load_bot_from_file(filename):

        with open(str(filename), "rb") as botsconfig_file:
            bot = pickle.load(botsconfig_file)
            unfreeze = jsonpickle.decode(bot)
            return unfreeze

    def save_single_bot_to_file(self, bot):

        filename = str(bot.name) + " " + str(bot.priceMarket.primaryCurrency) + \
            '/'+str(bot.priceMarket.secondaryCurrency)+'.haasbot'
        frozen = jsonpickle.encode(bot)

        currentfile = Path(str(filename))
        currentfile.touch(exist_ok=True)
        try:
            with open(filename, "wb") as botsconfig_file:
                pickle.dump(frozen, botsconfig_file)
            return frozen
        except Exception as e:
            print(e)
        return bot

    def save_configs_for_same_bot_to_file(self, botlist):
        print('Saving all the bots to a file')

        frozenbotlist = []
        filename = str(botlist[0].priceMarket.primaryCurrency) + \
            ''+str(botlist[0].priceMarket.secondaryCurrency) + '.haasbots'
        try:
            bots = self.load_botlist(filename)
            for bott in bots:
                frozenbotlist.append(jsonpickle.encode(bott))
        except:
            pass

        currentfile = Path(str(filename))
        currentfile.touch(exist_ok=True)

        for bot in botlist:
            # print(bot)
            frozenbotlist.append(jsonpickle.encode(bot))

        with open(filename, "wb") as botsconfig_file:
            pickle.dump(frozenbotlist, botsconfig_file)
        print(
            f'{botlist[0].name}: bot configs have been saved to file: {filename}')

    def load_botlist(self, dbfile):
        # Loads bot list from a
        botlist = []
        botlist2 = []
        with open(dbfile, "rb") as botsconfig_file:
            botlist = pickle.load(botsconfig_file)
            for bot in botlist:
                bot = jsonpickle.decode(bot)
                if type(bot) != str:
                    if bot.botType == 15:
                        # print(bot.name)
                        botlist2.append(bot)
        return botlist2

    def return_bot_from_bot_list(botlist2):
        botlist = []
        for bot in botlist2:

            print(bot.name)
            try:
                if bot.name:
                    botlist.append(bot)
            except AttributeError:
                # print(i,bot)
                pass

        for i, bot in enumerate(botlist):

            print(i, bot.roi, '% ROI with ', len(
                bot.completedOrders), ' trades')

        userinput = input('type but number to select')
        bot = botlist[int(userinput)]

        return bot

    def create_new_trade_bot(newbot, example_bot):
        new = self.c.tradeBotApi.new_trade_bot(
            example_bot.accountId,
            "imported " + newbot.name,
            newbot.priceMarket.primaryCurrency,
            newbot.priceMarket.secondaryCurrency,
            newbot.priceMarket.contractName,
            newbot.leverage,
            "",
        )
        print("error: ", new.errorCode, new.errorMessage)
        newr = new.result
        # print('NEW  \n',new)
        return newr

    def set_safety_parameters(newbot, example_bot):
        sellStep = self.c.customBotApi.set_mad_hatter_safety_parameter(
            newbot.guid, EnumMadHatterSafeties.PRICE_CHANGE_TO_SELL, example_bot.priceChangeToSell)
        print(sellStep.errorCode, sellStep.errorMessage)
        buyStep = self.c.customBotApi.set_mad_hatter_safety_parameter(
            newbot.guid, EnumMadHatterSafeties.PRICE_CHANGE_TO_BUY, example_bot.priceChangeToBuy)
        print(buyStep.errorCode, buyStep.errorMessage)
        stopLoss = self.c.customBotApi.set_mad_hatter_safety_parameter(
            newbot.guid, EnumMadHatterSafeties.STOP_LOSS, example_bot.stopLoss)
        print(stopLoss.errorCode, stopLoss.errorMessage)

    def all_mh_configs_to_csv(self, botlist):
        filename = str(datetime.datetime.today())+' ' + \
            str(len(botlist))+' Mad-Hatter-Bots.csv'
        with open(filename, "w", newline="") as csvfile:
            fieldnames = [
                "pricesource",
                "primarycoin",
                "secondarycoin",
                "interval",
                "signalconsensus",
                "fcc",
                "resetmiddle",
                "allowmidsells",
                "matype",
                "rsil",
                "rsib",
                "rsis",
                "bbl",
                "devup",
                "devdn",
                "macdfast",
                "macdslow",
                "macdsign",
                "roi"
            ]
            csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
            csvwriter.writeheader()
            for bot in botlist:
                csvwriter.writerow(
                    {
                        "pricesource": EnumPriceSource(bot.priceMarket.priceSource).name,
                        "primarycoin": bot.priceMarket.primaryCurrency,
                        "secondarycoin": bot.priceMarket.secondaryCurrency,
                        "interval": str(bot.interval),
                        "signalconsensus": str(bot.useTwoSignals),
                        "resetmiddle": str(bot.bBands["ResetMid"]),
                        "allowmidsells": str(bot.bBands["AllowMidSell"]),
                        "matype": str(bot.bBands["MaType"]),
                        "fcc": str(bot.bBands["RequireFcc"]),
                        "rsil": str(bot.rsi["RsiLength"]),
                        "rsib": str(bot.rsi["RsiOversold"]),
                        "rsis": str(bot.rsi["RsiOverbought"]),
                        "bbl": str(bot.bBands["Length"]),
                        "devup": str(bot.bBands["Devup"]),
                        "devdn": str(bot.bBands["Devdn"]),
                        "macdfast": str(bot.macd["MacdFast"]),
                        "macdslow": str(bot.macd["MacdSlow"]),
                        "macdsign": str(bot.macd["MacdSign"]),
                        "roi": str(bot.roi)
                    }
                )

            print(
                "All Bots have been sucessfully saved to a file in same folder as this app."
            )
        return filename

    def iterate_df_configs(self):
        bot = BotSellector().get_mad_hatter_bot()
        configs = self.csv_to_dataframe()
        uip = input(
            '\nType 1 to backtest bot with configs from file, \nType 2 to select config from a given file and apply it to bot\n\n Respose: ')

        if uip == '1':
            results = self.setup(bot, configs)
            BotDB().dataframe_to_csv(bot, results)

            results.sort_values(by='roi', ascending=False, inplace=True)
            results = self.user_selected_bot_config(bot, results)
        elif uip == '2':
            results = self.set_csv_config(bot, configs)

    def setup(self, bot, configs, index=None,):

        if index == None:
            for ind in configs.index:
                self.setup_bot_from_obj(bot, configs, ind)
                configs = self.bt_mh(bot, configs, ind)
                BotDB().dataframe_to_csv(bot, configs)
            return configs.sort_values(by='roi', ascending=False)
        else:
            self.setup_bot_from_obj(bot, configs, int(index))
            configs = self.bt_mh(bot, configs, int(index))
            BotDB().dataframe_to_csv(bot, configs)
            return configs.sort_values(by='roi', ascending=False)

    def user_selected_bot_config(self, bot, configs):
        while True:
            ind = input(
                '\nType bot number to apply given config to selected bot \nType X or x to select another bot. \n\n Response: ')
            if ind == 'X' or ind == 'x':
                self.iterate_df_configs()
            else:
                configs = self.setup(bot, configs, ind)

    def bt_mh_df(self, bot, configs, ind):
        bt = self.bt_mh_visible_roi(bot)
        print('BT ROI IS:', bt.roi)
        configs['roi'][int(ind)] = bt.roi
        configs['trades'][int(ind)] = len(bt.completedOrders)
        configs.sort_values(by='roi', ascending=False, inplace=True)
        self.dataframe_to_csv(bot, configs)
        print(configs.head(20))
        return configs

    def bt_mh(self, bot, configs, ind, ticks):

        bt = self.c.customBotApi.backtest_custom_bot_on_market(
            bot.accountId,
            bot.guid,
            int(ticks),
            bot.priceMarket.primaryCurrency,
            bot.priceMarket.secondaryCurrency,
            bot.priceMarket.contractName).result
        print('BT ROI IS:', bt.roi)
        configs['roi'][int(ind)] = bt.roi
        configs['trades'][int(ind)] = len(bt.completedOrders)
        configs.sort_values(
            by='roi', ascending=False, inplace=True)
        # self.save_configs_for_same_bot_to_file(bt)
        print(configs.head(20))
        return configs

    def setup_bot_from_obj(self, bot, configs, ind):
        if bot.bBands["Length"] != configs['bbl'][int(ind)]:
            do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                0,
                configs['bbl'][int(ind)]
            )

        if bot.bBands["Devup"] != configs['devup'][int(ind)]:
            do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                1,
                configs['devup'][int(ind)],
            )

        if bot.bBands["Devdn"] != configs['devdn'][int(ind)]:
            do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                2,
                configs['devdn'][int(ind)],
            )

        if bot.bBands["MaType"] != configs['matype'][int(ind)]:
            do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                3,
                configs['matype'][int(ind)],
            )

        if bot.bBands["AllowMidSell"] != configs['allowmidsells'][int(ind)]:
            do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                5,
                configs['allowmidsells'][int(ind)],
            )

        if bot.bBands["RequireFcc"] != configs['fcc'][int(ind)]:
            do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                6,
                configs['fcc'][int(ind)],
            )

        if bot.rsi["RsiLength"] != configs['rsil'][int(ind)]:
            do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.RSI,
                0,
                configs['rsil'][int(ind)],
            )

        if bot.rsi["RsiOverbought"] != configs['rsib'][int(ind)]:
            do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.RSI,
                1,
                configs['rsib'][int(ind)],
            )

        if bot.rsi["RsiOversold"] != configs['rsis'][int(ind)]:
            do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.RSI,
                2,
                configs['rsis'][int(ind)],
            )

        if bot.macd["MacdFast"] != configs['macdfast'][int(ind)]:
            do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.MACD,
                0,
                configs['macdfast'][int(ind)],
            )

        if bot.macd["MacdSlow"] != configs['macdslow'][int(ind)]:
            do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.MACD,
                1,
                configs['macdslow'][int(ind)],
            )

        if bot.macd["MacdSign"] != configs['macdsign'][int(ind)]:
            do = self.c.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.MACD,
                2,
                configs['macdsign'][int(ind)],
            )

        if bot.interval != configs['interval'][int(ind)]:
            setup_bot = self.c.customBotApi.setup_mad_hatter_bot(
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
                interval=configs['interval'][int(ind)],
                includeIncompleteInterval=bot.includeIncompleteInterval,
                mappedBuySignal=bot.mappedBuySignal,
                mappedSellSignal=bot.mappedSellSignal,).result

        print(bot.name, ' Has been configured')
        return do
    def bt_mh_visible_roi(self, current_bot):

        ticks = iiv.total_ticks()
        bt = self.c.customBotApi.backtest_custom_bot(
            current_bot.guid,
            int(ticks),
        )
        if bt.errorCode != EnumErrorCode.SUCCESS:
            print("bt", bt.errorCode, bt.errorMessage)
        else:
            print(bt.result.roi)
        return bt.result

    def csv_to_dataframe(self, csv=None):
        if csv == None:
            csv = self.get_csv_file()
            configs = pd.read_csv(csv)
            print(configs)
            return configs
        else:
            configs = pd.read_csv(csv)
            print(configs)
            return configs

    def dataframe_to_csv(self, bot, df):
        filename = f'{EnumPriceSource(bot.priceMarket.priceSource).name},{bot.priceMarket.primaryCurrency},{bot.priceMarket.secondaryCurrency}.csv'
        df.to_csv(filename)
        # self.save_configs_for_same_bot_to_file(df.botobject)
        print("Configs saved to csv for given mrket and pair")

    def setup_bot_from_csv(self, bot, csv):
        csv = sealf.get_csv_file()

    def set_csv_config(self, bot, configs):
        done = self.user_selected_bot_config(bot, configs)
        bt = self.bt_mh_visible_roi(bot)

def iterate_main():

    uip = input('Would you like to set backtesting date? (y/n): ')
    if uip == 'y' or uip == 'yes' or uip == 'Yes' or uip == 'YES' or uip == 'Y':
        configserver.set_bt()

    else:
        pass

    results = BotDB().iterate_df_configs()

if __name__ == "__main__":
    iterate_main()
