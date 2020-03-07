from threading import Timer
from threading import Thread
import botsellector
import configserver
import json
import os
from io import StringIO
from pathlib import Path
import base64, zlib, gzip
# from pastebinapi import PasteBin
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

ip, secret = configserver.validateserverdata()
haasomeClient = HaasomeClient(ip, secret)


class BotDB:
    def __init__(self):
        self.bot = None
        self.botlist = None
        self.db_file = None
        self.local_path = './'
        self.last_created_bot = None

    def get_haasbots_file(self):
        #Returns bot-containing list of files from home folder
        files = []
        for file in os.listdir('./'):
            if file.endswith(".haasbots"):
                files.append(os.path.join('./', file))
        for i, file in enumerate(files):
            print(i, file)
        userinput = input('Type file number to select it:  ')
        self.db_file = files[int(userinput)]
        return files[int(userinput)]
    def get_csv_file(self):
        files =[]
        for file in os.listdir('./'):
            if file.endswith(".csv"):
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
        #returns filepath to user specified file from the above list
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


    def save_single_bot_to_file(self,bot):
        #Save singie bot as a file.
        filename = str(bot.name)+ " "+ str(bot.priceMarket.primaryCurrency)+'/'+str(bot.priceMarket.secondaryCurrency)+'.haasbot'
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

    def save_configs_for_same_bot_to_file(self,botlist):
        #Saves given botlist to a file
        # botlist = sorted(botlist, key=lambda x: x.roi, reverse=True)
        print('Saving all the bots to a file')
        t = datetime.datetime.today()
        frozenbotlist = []
        filename = str(botlist[0].priceMarket.primaryCurrency) + \
            ''+str(botlist[0].priceMarket.secondaryCurrency)+ '.haasbots'
        # filename = str(t.strftime("%b %d %y ")+' '+str(botlist[0].priceMarket.primaryCurrency)+''+str(botlist[0].priceMarket.secondaryCurrency)+' '+str(len(botlist))+'bots,ROI:'+str(botlist[0].roi)+' .haasbots')
        # filename = f'{(botlist[0].guid)}.haasbots'
        try:
            bots = self.load_botlist(filename)
            for bot in bots:
             frozenbotlist = jsonpickle.encode(bot)
        except Exception as e:
           print(e)

        currentfile = Path(str(filename))
        currentfile.touch(exist_ok=True)

        for bot in botlist:
            print(bot)
            frozenbotlist.append(jsonpickle.encode(bot))


        with open(filename, "wb") as botsconfig_file:
            pickle.dump(frozenbotlist, botsconfig_file)
        print(f'{botlist[0].name}: bot configs have been saved to file: {filename}')



    def load_botlist(self,dbfile):
        #Loads bot list from a
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
        botlist= []
        for bot in botlist2:

            print(bot.name)
            try:
                if bot.name:
                    botlist.append(bot)
            except AttributeError:
                    # print(i,bot)
                pass
        # for i, bot in enumerate(botlist):
        #     try:
        #         print(i, bot.roi,'% ROI with ', len(bot.completedOrders),' trades')

        #     except AttributeError:
        #         # print(i,bot)
        #         bot = jsonpickle.decode(bot)
        #         print(i, bot.roi,'% ROI with ', len(bot.completedOrders),' trades')
        for i, bot in enumerate(botlist):

            print(i, bot.roi,'% ROI with ', len(bot.completedOrders),' trades')


        userinput = input('type but number to select')
        bot = botlist[int(userinput)]

        return bot

    def return_botlist_range(botlist):
        botlist2 = []
        for bot in botlist:
            if type(bot) == str:
             bot2 = jsonpickle.decode(bot)
             botlist2.append(bot2)
            else:
                pass

        for i, bot in enumerate(botlist2):
             print(i, bot.roi,'% ROI with ', len(bot.completedOrders),' trades')

        userinput = input('Type number of bots to recreate. From zero to: ')
        return (botlist[0:int(userinput)])



    def load_bot_from_file(filename):

        with open(str(filename), "rb") as botsconfig_file:
            bot = pickle.load(botsconfig_file)
            unfreeze = jsonpickle.decode(bot)
            return unfreeze



    def create_new_custom_bot(newbot, example_bot):
        new = haasomeClient.customBotApi.new_custom_bot(
            example_bot.accountId,
            newbot.botType,
            "IMP: " + newbot.name,
            newbot.priceMarket.primaryCurrency,
            newbot.priceMarket.secondaryCurrency,
            newbot.priceMarket.contractName,
        )
        print(new.errorCode, new.errorMessage)
        print(new.result)
        # print(new.result)
        # newr = new.result
        # print(newr)
        BotDB.set_safety_parameters(new.result, example_bot)
        return new.result

    def setup_mad_hatter_bot(current_bot, haasomeClient, interval):
        botname = str(current_bot.priceMarket.primaryCurrency) + str(' / ') + \
                    str(current_bot.priceMarket.secondaryCurrency) + str(' Roi ') + str(current_bot.roi)
        setup_bot = haasomeClient.customBotApi.setup_mad_hatter_bot(
        botName = current_bot.name,
        botGuid=current_bot.guid,
        accountGuid=current_bot.accountId,
        primaryCoin=current_bot.priceMarket.primaryCurrency,
        secondaryCoin=current_bot.priceMarket.secondaryCurrency,
        contractName=current_bot.priceMarket.contractName,
        leverage=current_bot.leverage,
        templateGuid=current_bot.customTemplate,
        position=current_bot.coinPosition,
        fee=current_bot.currentFeePercentage,
        tradeAmountType=current_bot.amountType,
        tradeAmount=current_bot.currentTradeAmount,
        useconsensus=current_bot.useTwoSignals,
        disableAfterStopLoss=current_bot.disableAfterStopLoss,
        interval=current_bot.interval,
        includeIncompleteInterval=current_bot.includeIncompleteInterval,
        mappedBuySignal=current_bot.mappedBuySignal,
        mappedSellSignal=current_bot.mappedSellSignal,).result
        print(current_bot.name,' Has been configured')
        return setup_bot.result

    def create_new_trade_bot(newbot, example_bot):
        new = haasomeClient.tradeBotApi.new_trade_bot(
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
        sellStep = haasomeClient.customBotApi.set_mad_hatter_safety_parameter(
            newbot.guid, EnumMadHatterSafeties.PRICE_CHANGE_TO_SELL, example_bot.priceChangeToSell)
        print(sellStep.errorCode,sellStep.errorMessage)
        buyStep = haasomeClient.customBotApi.set_mad_hatter_safety_parameter(
            newbot.guid, EnumMadHatterSafeties.PRICE_CHANGE_TO_BUY, example_bot.priceChangeToBuy)
        print(buyStep.errorCode,buyStep.errorMessage)
        stopLoss = haasomeClient.customBotApi.set_mad_hatter_safety_parameter(
            newbot.guid, EnumMadHatterSafeties.STOP_LOSS, example_bot.stopLoss)
        print(stopLoss.errorCode,stopLoss.errorMessage)

    def split_csv(self, chunks):
        file = self.get_csv_file()


    def all_mh_configs_to_csv(botlist):
        filename = str(datetime.datetime.today())+' '+str(len(botlist))+' Mad-Hatter-Bots.csv'
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
                    }
                )

            print(
                "All Bots have been sucessfully saved to a file in same folder as this app."
            )





    def iterate_df_configs(self):
        botlist = botsellector.return_all_mh_bots(haasomeClient)
        bot = botsellector.get_specific_bot(haasomeClient, botlist)
        configs = self.csv_to_dataframe()
        # configs.drop(columns=['pricesource','primarycoin','secondarycoin'])
        results = self.setup(bot, configs)
        BotDB().dataframe_to_csv(bot, results)
        results.sort_values(by='roi', ascending=False, inplace=True)
        btsts = self.user_selected_bot_config(bot, results)

        return results


    def setup(self, bot,configs, index = None):

        if index == None:
            for ind in configs.index:

                print(ind)
                configs = self.setup_bot(bot, configs, ind)
        else:
            configs = self.setup_bot(bot,configs,str(index))
        return configs.sort_values(by='roi', ascending=False)
    def user_selected_bot_config(self, bot, configs):
        while True:
            ind = input('Type bot number to apply given config to selected bot or type X or x to select another bot: ')
            if ind == 'X' or ind == 'x':
               self.iterate_df_configs()
            else:
                configs = self.setup(bot, configs, ind)
                bt = self.bt_mh_visible_roi(bot)



    def setup_bot(self,bot,configs,ind,):
            if bot.bBands["Length"] != configs['bbl'][int(ind)]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                0,
                    configs['bbl'][int(ind)]
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    # pass
                    print(do.erro/rCode, do.errorMessage, 'Length')
            except:
                pass
            if bot.bBands["Devup"] != configs['devup'][int(ind)]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.BBANDS,
                    1,
                    configs['devup'][int(ind)],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'Devup')
                except:
                    pass
            if bot.bBands["Devdn"] != configs['devdn'][int(ind)]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.BBANDS,
                    2,
                    configs['devdn'][int(ind)],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                            pass
                            print(do.errorCode, do.errorMessage, 'Devdn')
                except:
                    pass
            if bot.bBands["MaType"] != configs['matype'][int(ind)]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.BBANDS,
                    3,
                    configs['matype'][int(ind)],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'MaType')
                except:
                    pass
            if bot.bBands["AllowMidSell"] != configs['allowmidsells'][int(ind)]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.BBANDS,
                    5,
                    configs['allowmidsells'][int(ind)],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'AllowMidSell')
                except:
                    pass
            if bot.bBands["RequireFcc"] != configs['fcc'][int(ind)]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.BBANDS,
                    6,
                    configs['fcc'][int(ind)],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'RequireFcc')
                except:
                    pass
            if bot.rsi["RsiLength"] != configs['rsil'][int(ind)]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.RSI,
                    0,
                    configs['rsil'][int(ind)],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'RsiLength')
                except:
                    pass
            if bot.rsi["RsiOverbought"] != configs['rsib'][int(ind)]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.RSI,
                    1,
                    configs['rsib'][int(ind)],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'RsiOverbought')
                except:
                    pass
            if bot.rsi["RsiOversold"] != configs['rsis'][int(ind)]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.RSI,
                    2,
                    configs['rsis'][int(ind)],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'RsiOversold')
                except:
                    pass
            if bot.macd["MacdFast"] != configs['macdfast'][int(ind)]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.MACD,
                    0,
                    configs['macdfast'][int(ind)],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'MacdFast')
                except:
                    pass
            if bot.macd["MacdSlow"] != configs['macdslow'][int(ind)]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.MACD,
                    1,
                    configs['macdslow'][int(ind)],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'MacdSlow')
                except:
                    pass

            if bot.macd["MacdSign"] != configs['macdsign'][int(ind)]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.MACD,
                    2,
                    configs['macdsign'][int(ind)],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'MacdSign')
                except:
                    pass
            if bot.interval != configs['interval'][int(ind)]:
                botname = str(bot.priceMarket.primaryCurrency) + str(' / ') + \
                    str(bot.priceMarket.secondaryCurrency) + str(' Roi ') + str(bot.roi)
                setup_bot = haasomeClient.customBotApi.setup_mad_hatter_bot(
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
                interval=configs['interval'][int(ind)],
                includeIncompleteInterval=bot.includeIncompleteInterval,
                mappedBuySignal=bot.mappedBuySignal,
                mappedSellSignal=bot.mappedSellSignal,).result
                # print(bot.name,' Has been configured')

            else:
                print(bot.name,' Has been configured')
            bt = self.bt_mh(bot)
            configs['roi'][int(ind)] = bt.roi
            configs.sort_values(by='roi', ascending=False, inplace=True)
            print(configs.head(20))
            return configs

    def bt_mh(self,current_bot):

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

    def bt_mh_visible_roi(self, current_bot):

        ticks = iiv.total_ticks(current_bot)
        bt = haasomeClient.customBotApi.backtest_custom_bot(
            current_bot.guid,
            int(ticks),
        )
        if bt.errorCode != EnumErrorCode.SUCCESS:
            print("bt", bt.errorCode, bt.errorMessage)
        else:
            print(bt.result.roi)
        return bt.result

    def csv_to_dataframe(self):
        csv = self.get_csv_file()
        configs = pd.read_csv(csv)
        print(configs)
        return configs

    def dataframe_to_csv(self, bot, df):
        filename = f'{EnumPriceSource(bot.priceMarket.priceSource).name},{bot.priceMarket.primaryCurrency},{bot.priceMarket.secondaryCurrency}.csv'
        df.to_csv(filename, index_label='index', )
        print("Configs saved to csv for given mrket and pair")
    def setup_bot_from_csv(self, bot, csv):
        csv = sealf.get_csv_file()

    def jsavebots(botlist, file):
        frozenobjlist = []
        for i, bot in enumerate(botlist):
            frozen = json.dumps(bot)
            frozenobjlist.append(frozen)
        with open(file, "w") as f:
            json.dump(frozenobjlist, f)


    def jloadbots(file):
        with open(file, "r") as f:
            bots = json.load(f)
            return bots


    def print_keys(kl):
        if kl == i.bBands.keys():
            for key in kl:
                print("config.bBands['" + key + "']")
        if kl == i.macd.keys():
            for key in kl:
                print("config.macd['" + key + "']")
        if kl == i.rsi.keys():
            for key in kl:
                print("config.rsi['" + key + "']")







# def main2():
#     # botlist = BotDB.load_botlist("bots.db")
#     # all_mh_configs_to_csv(botlist)


# def main3():

#     bot = botsellector.getallbots(haasomeClient)
#     print(
#         "This is a simple script that uses a single file named bot.json for easy storage and sharing of Custom bots and Trade Bots. Its simple: select a bot to save, select save - bot saved to bot.json file. On another machine, select example bot, hit load bot and the bot will be recreated based on example bot account data."
#     )
#     print("1. Save a single bot to file")
#     print("2. Load bot from file")

#     user_response = input("Type number here: ")
#     if user_response == "1":

#         botdata = BotDB.save_single_bot_to_file(bot)
#         tada = to_pastebin(botdata)

#     if user_response == "2":
#         botstr = BotDB.load_bot_from_file()
#         bot2 = create_new_custom_bot(botstr, bot)

#     # bot = botsellector.getallbots(haasomeClient)
#     # string =	bot_to_string(bot)
#     # bot2 = make_bot_from_string(string)
    # print(bot2.botType)
    # clone = create_new_custom_bot(bot2, bot)


def main2():
    botlist = botsellector.return_all_mh_bots(haasomeClient)
    configs = BotDB.all_mh_configs_to_csv(botlist)

def main3():
    # BotDB().csv_to_dataframe()
    uip = input('Would you like to set backtesting date? (y/n): ')
    if uip == 'y' or uip == 'yes' or uip =='Yes' or uip =='YES' or uip == 'Y':
        configserver.set_bt()
    else:
        pass
    results = BotDB().iterate_df_configs()

def main1():
    botlist = botsellector.return_all_mh_bots(haasomeClient)

    bot = botsellector.get_specific_bot(haasomeClient,botlist)
    db_file = BotDB.get_haasbots_file()
    # print(db_file)

    bots_from_file = BotDB.load_botlist(BotDB.get_haasbots_file())
    # print(bots_from_file)
    # selected_bots = BotDB.return_botlist_range(bots_from_file)
    selected_bot = BotDB.return_bot_from_bot_list(bots_from_file)
    print(selected_bot.name)

    # selected_bots = BotDB.return_botlist_range(bots_from_file)
    # print(len(selected_bots),' bots are selected')
    # for i in selected_bots:
    #     ii = BotDB.make_bot_from_string(i)
    #     BotDB.create_new_custom_bot(bot,ii)
    # for i in  selected_bots:
    #   print(i.name)
    # print(selected_bot)

    # save = BotDB.save_single_bot_to_file()
    # load = BotDB.load_bot_from_file('bots.db')
    # print(load)

# def main2():
#     # db_file = BotDB.get_haasbots_file()
#     bots_from_file = BotDB.load_botlist(db_file)
#     bot = BotDB.return_bot_from_bot_list(bots_from_file)
#     ebot = botsellector.get_mh_bot(haasomeClient)
#     newbot = BotDB.create_new_custom_bot(bot,ebot)

# def main3():
#      db_file = BotDB.get_haasbots_file()
#      bots_from_file = BotDB.load_botlist(db_file)
#     #  j_save = jsavebots(bots_from_file, 'jsave.db')
#     #  bots_from_file = jloadbots(jsave.db)
#     #  print(bots_from_file)

# def main():
#     db_file = BotDB.get_haasbots_file()
#     bots_from_file = BotDB.load_botlist(db_file)
#     for b in bots_from_file:
#         if type(b) != str:
#             print(b.name)
#         # for k in b:
# #         #     print(k)
if __name__ == "__main__":
    main3()
    # main_save_all_mh()
