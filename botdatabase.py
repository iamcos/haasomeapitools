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

import time
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
from haasomeapi.HaasomeClient import HaasomeClient
from haasomeapi.enums.EnumMadHatterSafeties import EnumMadHatterSafeties

ip, secret = configserver.validateserverdata()
haasomeClient = HaasomeClient(ip, secret)


class BotDB:
    def __init__(self):
        self.bot = None
        self.botlist = None
        self.db_file = None
        self.local_path = './'
        self.last_created_bot = None

    def return_botlist_files(self):
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


    def setup_mad_hatter_bot(current_bot, haasomeClient):
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
    def strings_to_bots(selected_bots):
        bots = []
        print(len(selected_bots),' bots are selected')
        for i in selected_bots:
            ii = jsonpickle.decode(i)
            bots.append(ii)






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



def main1():
    botlist = botsellector.return_all_mh_bots(haasomeClient)
    bot = botsellector.get_specific_bot(haasomeClient,botlist)
    db_file = BotDB.return_botlist_files()
    # print(db_file)

    bots_from_file = BotDB.load_botlist(BotDB.return_botlist_files())
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
#     # db_file = BotDB.return_botlist_files()
#     bots_from_file = BotDB.load_botlist(db_file)
#     bot = BotDB.return_bot_from_bot_list(bots_from_file)
#     ebot = botsellector.get_mh_bot(haasomeClient)
#     newbot = BotDB.create_new_custom_bot(bot,ebot)

# def main3():
#      db_file = BotDB.return_botlist_files()
#      bots_from_file = BotDB.load_botlist(db_file)
#     #  j_save = jsavebots(bots_from_file, 'jsave.db')
#     #  bots_from_file = jloadbots(jsave.db)
#     #  print(bots_from_file)

# def main():
#     db_file = BotDB.return_botlist_files()
#     bots_from_file = BotDB.load_botlist(db_file)
#     for b in bots_from_file:
#         if type(b) != str:
#             print(b.name)
#         # for k in b:
# #         #     print(k)
# if __name__ == "__main__":
#     main2()
#     main_save_all_mh()
