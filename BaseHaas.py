import base64
import configparser as cp
import csv
import datetime
import gzip
import json
import os
import pickle
import time
import timeit
import zlib
from tqdm import tqdm
from tqdm.auto import trange
# from datetime import datetime
import datetime
from functools import lru_cache
from pathlib import Path
from random import random
from time import sleep
from prompt_toolkit.validation import Validator, ValidationError
from haasomeapi.apis.AccountDataApi import AccountDataApi as acc
# import jsonpickle
import pandas as pd
import requests
from haasomeapi.enums.EnumCustomBotType import EnumCustomBotType
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from haasomeapi.enums.EnumIndicator import EnumIndicator
from haasomeapi.enums.EnumMadHatterIndicators import EnumMadHatterIndicators
from haasomeapi.enums.EnumMadHatterSafeties import EnumMadHatterSafeties
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
from haasomeapi.HaasomeClient import HaasomeClient
from numpy import arange
import numpy as np
# from PyInquirer import (Token, prompt)
from ratelimit import limits, sleep_and_retry
# from autobt import InteractiveBT
import configserver
import interval as iiv
# from botdb import BotDB
from botsellector import BotSellector
import inquirer
from alive_progress import alive_bar
import logging
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Haas():

    """
    Haasonline trading software interaction class: get botlist, marketdata, create bots and configure their parameters, initiate backtests and so forth can be done through this class
    """

    def __init__(self):
        self.c = self.client()

    def client(self):
        ip, secret = self.read_config()
        haasomeClient = HaasomeClient(ip, secret)
        haasomeClient.test_credentials().errorCode
        return haasomeClient

    def read_config(self):
        c = cp.ConfigParser()
        try:
            c.read('config.ini')
        except Exception as e:
            print(e)
            self.test_config()
        else:
            try:
                ip = c['SERVER DATA']['server_address']
                secret = c['SERVER DATA']['secret']
            except Exception as e:
                print(e)
                self.test_config()
        finally:
            ip = c['SERVER DATA']['server_address']
            secret = c['SERVER DATA']['secret']
        return ip, secret

    def read_cfg(self):
        c = cp.ConfigParser()
        c.read('config.ini')
        return c

    def write_date(self):
        c = self.read_cfg()

        choices = [f'Write Year:', f'Write month (current is {str(datetime.datetime.today().month)}): ', f'Write day (today is {str(datetime.datetime.today().day )}: ',
                   f'Write  hour (now is {str(datetime.datetime.today().hour)}):', f'Write min ( mins now {str(datetime.datetime.today().minute)}): ']

        date_q = [inquirer.Text('y', message=choices[0]),
                  inquirer.Text('m', message=choices[1]),
                  inquirer.Text('d', message=choices[2]),
                  inquirer.Text('h', message=choices[3]),
                  inquirer.Text('min', message=choices[4])]

        # menu = [inquirer.List('response', message = "Go through each step",choices = choices)]
        answers = inquirer.prompt(date_q)

        c['BT DATE'] = {'year': answers['y'], 'month': answers['m'],
                        'day': answers['d'], 'hour': answers['h'], 'min': answers['min']}
        with open('config.ini', 'w') as configfile:
            c.write(configfile)

    def read_ticks(self):
        c = self.read_cfg()
        try:
            min = c['BT DATE'].get('min')
            hour = c['BT DATE'].get('hour')
            day = c['BT DATE'].get('day')
            month = c['BT DATE'].get('month')
            year = c['BT DATE'].get('year')
            print('BT date set to: ', year, month, day, hour, min)
            dt_from = datetime.datetime(int(year), int(
                month), int(day), int(hour), int(min))
            delta = datetime.datetime.now() - dt_from
            delta_minutes = delta.total_seconds()/60
        except KeyError:
            date = self.write_date()
            min = c['BT DATE'].get('min')
            hour = c['BT DATE'].get('hour')
            day = c['BT DATE'].get('day')
            month = c['BT DATE'].get('month')
            year = c['BT DATE'].get('year')
            print('BT date set to: ', year, month, day, hour, min)
            dt_from = datetime.datetime(int(year), int(
                month), int(day), int(hour), int(min))
        delta = datetime.datetime.now() - dt_from
        delta_minutes = delta.total_seconds()/60

        return int(delta_minutes)

    def test_config(self):

        c = cp.ConfigParser()
        try:
            c.read('config.ini')
            ip = c['SERVER DATA']['server_address']
            secret = c['SERVER DATA']['secret']
            test = self.client(ip, secret)
            print(test.test_credentials().errorMessage.__dict__,
                  test.test_credentials().errorCode.value)
            if test.test_credentials().errorCode.value == EnumErrorCode.SUCCESS:
                print('Connected to Haas')
                return ip, secret
            else:
                print(
                    f'Something isn not right. {test.test_credentials().errorCode}')

        except Exception as e:
            print(e)
            self.configure_haas()

    def configure_haas(self):

        apiSetup = [

            inquirer.Confirm(
                'apiConfigured', 'Have you configured Haas Online API on the client side?')

        ]

        setup = inquirer.prompt(apiSetup)

        if not setup['apiConfigured']:
            print(f'Following is a step by step guide to configure Haas Local Api. After doing each step, type Y on keyboard to get to next step. \n')
            config_questions = [
                inquirer.Text('settingsPage', 'Open HaasOnline Settings page'),

                inquirer.Text('apiSettingsPage',
                              'Navigate to Local Api page in Settings'),

                inquirer.Text(
                    'inputIP', 'Input IP. If this app on the same server type:127.0.0.1, else: server address that you use to access Haas remotely'),


                inquirer.Text(
                    'inputPort', 'Input Port Number in the next field. Can be any number, for instance 8095'),


                inquirer.Text(
                    'inputSecret', 'Input API key in the next field. If app running on the same server, can be simple.  Else, make it complicated'),


                inquirer.Text(
                    'saveClicked', 'Click save at the bottom of the page and wait for Haas to do its thing.'),

                inquirer.Text(
                    'passwordSavedAgain', 'Once Haas done its thing, go back to Settings > Local API page and check that password field is not empty. If empty, enter it again and hit save again'),


                inquirer.Text('restarted', 'Once saved, restart Haas server. If running on windows, check if there is any mentions of Local API server in the console app. App will test the connection itself at a later stage'),
                inquirer.Text(
                    'apiActivated', 'API should be activated, Now lets input API data into the app. This only needs to be done once.'),

            ]
        configuredAPI = inquirer.prompt(config_questions)

        server_api_data = [

            inquirer.Text('ip',
                          'Type Haas Local api IP like so: 127.0.0.1',
                          default='127.0.0.1'),
            inquirer.Text('port',
                          'Type Haas Local api PORT like so: 8095',
                          default='8095'),
            inquirer.password('secret',
                              'Type Haas Local Key (Secret) like so: 123',
                              default='123')]
        connection_data = inquirer.prompt(server_api_data)
        print(connection_data)
        c = cp.ConfigParser()
        c['SERVER DATA'] = {'server_address': 'http://'+connection_data['ip'] +
                            ':'+connection_data['port'], 'secret': connection_data['secret']}
        with open('config.ini', 'w') as configfile:
            c.write(configfile)
        return connection_data


class Bot(Haas):
    def __init__(self):
        Haas.__init__(self)


class Main_Menu(Haas):
    def __init__(self):
        Haas.__init__(self)
        self.bot = None
        self.file = None
        self.configs = None

    def main_screen(self):

        choices = [
            'Find and save good configs: AssistedBT',
            "Bruteforce Scalper Bots (bonus feature)",
            'Autobacktest multiple bots',
            'Select and apply config to bot',
            'Change backtesting starting date',
            'Change AssistedBT loop Count',
            'Development Features',
            'Quit'

        ]
        loop_count = 10

        # os.system('clear')
        questions = [
            inquirer.List('resp', 'Select an option using keyboard up and down keys, then hit Return : ', choices=choices)]

        while True:
            try:
                answers = inquirer.prompt(questions)

                if answers['resp'] in choices:
                    ind = choices.index(answers['resp'])
                    # print(ind,str(ind))
                else:
                    raise Exception('Selected Option is not available')
                if ind == 0:
                    BT = InteractiveBT().backtest(loop_count)
                elif ind == 1:
                    scalper_test_menu()
                elif ind == 2:
                    bt = self.multiple_bot_auto_bt_menu()
                elif ind == 3:
                    self.apply_configs_menu()
                elif ind == 4:
                    c = Haas().read_cfg()
                    Haas().write_date()
                elif ind == 5:
                    loop_count = input('Type New Loop Count: ')
                    print(f'Auto BT lool count has been set to: {loop_count}')
                elif ind == 6:
                    file = self.dev_features()
                elif ind == 7:
                    break
            except KeyError:
                # os.system('clear')
                # print('\n\n     Mouse is not supported, use keyboard instead.\n\n')
                pass
        return answers

    def dev_features(self):
        question = [inquirer.List('resp', 'Select Something', [
                                  'Create Scalper bots from Tradingview CSV file', 'Create Mad-Hatter bots from Tradingview CSV file','Create Ping-Pong bots from Tradingview CSV file', 'Create Order Bots bots from Tradingview CSV file'])]
        answer = inquirer.prompt(question)
        if answer['resp'] == 'Create Scalper bots from Tradingview CSV file':
            new_bots = self.tw_to_bots(3)
        elif answer['resp'] == 'Create Mad-Hatter bots from Tradingview CSV file':
            new_bots = self.tw_to_bots(15)
        elif answer['resp'] == 'Create Ping-Pong bots from Tradingview CSV file':
            new_bots = self.tw_to_bots(2)
        elif answer['resp'] == 'Create Order Bots bots from Tradingview CSV file':
            new_bots = self.tw_to_bots(4)
    
    
    def tw_to_bots(self,bottype):
    
        markets_df = self.return_marketobjects_from_tradingview_csv_file()
        accounts_with_details = self.tw_to_haas_market_translator()
        botlist = self.c.customBotApi.get_all_custom_bots().result
        for m in markets_df.marketobj.values:
            for a in accounts_with_details:
                if m.priceSource == a.connectedPriceSource:
                    try:
                        bot = self.create_bots_from_tradingview_screener(bottype, m, a)
                        
                        print(
                            f'{len(bot)} has been created for {EnumPriceSource[m.priceSource].name}')
                    except Exception as e:
                        print(e)
        botlist2 = self.c.customBotApi.get_all_custom_bots().result
        newbots = []
        for bot in botlist2:
            if bot not in botlist:
                self.setup_bot(bot,bottype,m)
                newbots.append(bot)
        sb = ScalperBotClass()

        sb.bot = newbots
        sb.targetpercentage = [0.5,5,0.2]
        sb.safetythreshold = [1,5,0.2]
        sb.backtest()
        

    def tw_to_haas_market_translator(self):    
        
        accounts = self.c.accountDataApi.get_all_account_details().result
        accounts_guid = list(accounts.keys())

        accounts_with_details = []
        for a in accounts_guid:
            acc = self.c.accountDataApi.get_account_details(a).result
            accounts_with_details.append(acc)
        return accounts_with_details


    def create_bots_from_tradingview_screener(self, EnumBot, market_object, account):
        
        newbot = self.c.customBotApi.new_custom_bot(
            account.guid, EnumBot, f'TW {market_object.primaryCurrency}/{market_object.secondaryCurrency}', market_object.primaryCurrency, market_object.secondaryCurrency, market_object.contractName).result
        return newbot
    
    def setup_bot(self,bot,EnumBot,priceMarket):
            
            
            
            if EnumBot == 15:
                setup = self.c.customBotApi.setup_mad_hatter_bot(
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
                tradeAmount=1000,
                useconsensus=bot.useTwoSignals,
                disableAfterStopLoss=bot.disableAfterStopLoss,
                interval=bot.interval,
                includeIncompleteInterval=bot.includeIncompleteInterval,
                mappedBuySignal=bot.mappedBuySignal,
                mappedSellSignal=bot.mappedSellSignal).result
            elif EnumBot == 3:
                setup = self.c.customBotApi.setup_scalper_bot(
                botname=bot.name,
                botguid=bot.guid,
                accountguid=bot.accountId,
                primarycoin=bot.priceMarket.primaryCurrency,
                secondarycoin=bot.priceMarket.secondaryCurrency,
                contractname=bot.priceMarket.contractName,
                leverage=bot.leverage,
                templateguid=bot.customTemplate,
                position=bot.coinPosition,
                fee=bot.currentFeePercentage,
                amountType=bot.amountType,
                tradeamount=1000,
                targetpercentage = 10,
                safetythreshold = 5
                )
            elif EnumBot == 4:
                setup = self.c.customBotApi.setup_order_bot(
                botname=bot.name,
                botguid=bot.guid,
                accountguid=bot.accountId,
                primarycoin=bot.priceMarket.primaryCurrency,
                secondaryCoin=bot.priceMarket.secondaryCurrency,
                ).result
            elif EnumBot == 2:
                setup = self.c.customBotApi.setup_ping_pong_bot(
                botname=bot.name,
                botguid=bot.guid,
                accountguid=bot.accountId,
                primarycoin=bot.priceMarket.primaryCurrency,
                secondarycoin=bot.priceMarket.secondaryCurrency,
                ).result
            
    def return_marketobjects_from_tradingview_csv_file(self):
        tw_df = self.format_tw_csv()
        markets = MarketData().get_all_markets()
        '''
        Merging databases into one that contains data from both
        '''
        combined_df = pd.merge(tw_df, markets, how='outer', indicator='Exist')
        combined_df = combined_df.loc[combined_df['Exist'] == 'both']

        # print(len(combined_df.index)-len(tw_df.index),'from Tradingview csv were not identified')
        missing = pd.merge(tw_df,combined_df, how='outer', indicator='Missing')
        missing = missing.loc[missing['Missing'] != 'both']
        
        #prints combined lisst of tickers from tw and combined db
        # print(list(zip(tw_df.sort_values(by='Ticker', ascending=False)['Ticker'].values,combined_df.sort_values(by='Ticker', ascending=False)['Ticker'].values)))
        # print('tw_df',len(tw_df),'markets',len(markets),'combined_df',len(combined_df),'missing',len(missing))
        return combined_df
        
        
        
        


    def format_tw_csv(self):
        tw = pd.read_csv(self.file_selector('./tradingview'))
        # print(tw.columns)
        tw2 = pd.DataFrame()
        tw2['Ticker'] = tw['Ticker']
        Exchange = tw['Exchange'].values
        priceSources = []
        for i in Exchange:
            priceSources.append(EnumPriceSource[i].value)
        tw2['pricesource'] = priceSources
        # print(tw2)
        return tw2
        

    def apply_configs_menu(self):
        options = ['Select Bot', 'Select file with configs',
                   'Apply configs', 'Main Menu']
        config_questions = [inquirer.List(
            'response',
            'Select an option: ',
            options)]

        while True:
            response = inquirer.prompt(config_questions)
            if response['response'] in options:
                ind = options.index(response['response'])
            if ind == 0:
                bot = self.bot_selector()
            elif ind == 1:
                file = pd.read_csv(self.file_selector())
            elif ind == 2:
                # print(self.configs)

                configs = self.configs.sort_values(by='roi', ascending=False)
                configs.drop_duplicates()
                configs.reset_index(inplace=True, drop=True)
                while True:
                    print(configs)
                    print(
                        'To apply bot type config number from the left column and hit return.')
                    print('To return to the main menu, type q and hit return')
                    resp = input('Config number: ')
                    try:
                        if int(resp) >= 0:

                            BotDB().setup_bot_from_csv(
                                self.bot, configs.iloc[int(resp)])
                            # print(Haas().read_ticks)
                            BotDB().bt_bot(self.bot, Haas().read_ticks())
                        else:
                            break
                    except ValueError as e:
                        break

            elif ind == 3:
                break

    def auto_bt_menu(self):
        self.num_configs = 200
        options = ['Select Bot', 'Select config file',
                   'Set Limit', 'Start Backtesting', 'Main Menu']
        question = [inquirer.List(
            'autobt',
            'Select action: ',
            options)
        ]

        while True:
            response = inquirer.prompt(question)
            if response['autobt'] in options:
                ind = options.index(response['autobt'])
            if ind == 0:
                bot = self.bot_selector()
            elif ind == 1:
                file = pd.read_csv(self.file_selector())
            elif ind == 2:
                self.num_configs = int(
                    input('Type the number of configs you wish to apply from a given file: '))
            elif ind == 3:
                if self.num_configs > len(self.configs.index):
                    self.num_configs == len(self.configs.index)
                else:
                    pass
                configs = self.configs.sort_values(by='roi', ascending=False)[
                    0:self.num_configs]
                configs.drop_duplicates()
                configs.reset_index(inplace=True, drop=True)
                print(configs)
                bt_results = BotDB().iterate_csv(configs, self.bot, depth=Haas().read_ticks())
                filename = str(bot.name.replace('/', '_'))+str("_")+str(datetime.date.today().month)+str(
                    '-')+str(datetime.date.today().day)+str("_")+str(len(bt_results))+str('.csv')
                bt_results.to_csv(filename)
            elif ind == 4:
                break

    def multiple_bot_auto_bt_menu(self):
        self.num_configs = 200
        self.limit = 3
        menu = [inquirer.List('response', message='Please chose an action:', choices=[
                              'Select Bots', 'Select config file', 'Set configs limit', 'Set create limit', 'Start Backtesting', 'Main Menu'])]

        while True:
            user_response = inquirer.prompt(menu)['response']
            if user_response == 'Select Bots':
                bot = self.multiple_bot_sellector()
            elif user_response == 'Select config file':
                file = pd.read_csv(self.file_selector())
            elif user_response == 'Set configs limit':
                try:

                    num_configs = [inquirer.Text(
                        'num_configs', message='Type the number of configs you wish to apply from a given file: ')]
                    self.num_configs = int(
                        inquirer.prompt(num_configs)['num_configs'])
                except ValueError:
                    print(
                        'Invalid input value for the number of configs to apply from a given file. Please type a digit:')
                    num_configs = [inquirer.Text(
                        'num_configs', message='Type the number of configs you wish to apply from a given file: ')]
                    self.num_configs = int(
                        inquirer.prompt(num_configs)['num_configs'])

            elif user_response == 'Set create limit':
                create_limit = [inquirer.Text(
                    'step', message='Type how many top bots to create ')]
                create_limit_response = inquirer.prompt(create_limit)['step']
                self.limit = int(create_limit_response)

                if int(self.limit) >= 1:
                    pass
                else:
                    self.limit = 0

            elif user_response == 'Start Backtesting':
                self.bt()
            elif user_response == 'Main Menu':
                break

    def finetune(self, bot):
        config = self.bot_config(bot)
        config.drop(['interval', 'signalconsensus', 'resetmiddle', 'allowmidsells',
                     'matype', 'fcc', 'trades', 'roi'], axis='columns', inplace=True)
        columns = config.columns
        tuning_configs = pd.DataFrame(columns=columns)
        for i in config.columns:
            v = config.i.values
            if int(v):
                if v >= 5:
                    for n in range(v, v+3, 1):
                        pass
                    for n in range(v-3, v, 1):
                        pass
                elif v <= 2:
                    pass
                elif v < 5:
                    for n in range(v, v+3):
                        pass
                    for n in range(v-2, v, 1):
                        pass

    def bt(self):
        for b in self.bot:
            if self.num_configs > len(self.configs.index):
                self.num_configs == len(self.configs.index)
            else:
                pass

            configs = self.configs.sort_values(by='roi', ascending=False)[
                0:self.num_configs]
            configs.drop_duplicates()
            configs.reset_index(inplace=True, drop=True)
            # print(configs)
            bt_results = BotDB().iterate_csv(configs, b, depth=Haas().read_ticks())
            filename = str(b.name.replace('/', '_'))+str("_")+str(datetime.date.today().month)+str(
                '-')+str(datetime.date.today().day)+str("_")+str(len(bt_results))+str('multi.csv')
            bt_results.sort_values(by='roi', ascending=False, inplace=True)
            bt_results.drop_duplicates()
            bt_results.reset_index(inplace=True, drop=True)
            bt_results.to_csv(filename)
            if self.limit:
                for c in range(self.limit):
                    new_bot = MadHatterBot().c.customBotApi.clone_custom_bot_simple(
                        b.accountId, b.guid, b.name).result
                    # print(new_bot)
                    new_bot = BotDB().bt_bot(new_bot, Haas().read_ticks())
                    BotDB().setup_bot_from_csv(new_bot, bt_results.iloc[c])

    def bot_selector(self):
        botlist = [{'value': i.guid, 'name': f"{i.name},'Orders:'{len(i.completedOrders)},'Roi: ',{i.roi}\n\n"} for i in MadHatterBot(
        ).return_botlist()]
        question = [inquirer.Checkbox(
            'bots', message='Select one or more bots using spacebar and then press return', choices=botlist)]
        selection = inquirer.prompt(question)
        for b in MadHatterBot().return_botlist():
            if selection['bots'] == b.guid:
                self.bot = b
        return self.bot

    def multiple_bot_sellector(self):
        print('BB')
        bots = MadHatterBot().return_botlist()
        b2 = [(f'{i.name} {i.priceMarket.primaryCurrency}-{i.priceMarket.secondaryCurrency}, {i.roi}', i)
              for i in bots]
        print('BB')
        question = [inquirer.Checkbox(
            'bots', message='Select one or more bots using spacebar and then press return', choices=b2)]
        selection = inquirer.prompt(question)
        try:
            self.bot = selection['bots']
        except TypeError:
            print('No bot has been selected, you must select one')
            self.multiple_bot_sellector()
        return selection['bots']

    def file_selector(self, path='.'):
        files = BotDB().get_csv_files(path)
        # print(files[0:5])
        question = [inquirer.List('file',
                                  'Please Select file from list: ',
                                  [i for i in files])]

        selection = inquirer.prompt(question)
        self.file = selection['file']
        self.configs = BotDB().read_csv(self.file)
        return self.file


class MadHatterBot(Bot):

    def create_mh(self, input_bot, name):
        new_mad_hatter_bot = self.c.customBotApi.new_mad_hatter_bot_custom_bot(
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
        bl = self.c.customBotApi.get_all_custom_bots().result
        botlist = [x for x in bl if x.botType == 15]

        return botlist

    def make_bot_from_bot_config(self, config, name):
        botname = (
            str(config.priceMarket.primaryCurrency)
            + str(" / ")
            + str(config.priceMarket.secondaryCurrency)
            + str(" Roi ")
            + str(config.roi))
        new_bot = self.create_mh(example_bot, botname)
        self.configure_mh_from_another_bot(config, new_bot)
        return new_bot.result

    def bruteforce_indicators(self, bot):

        d = self.bruteforce_rsi_corridor(bot)

    def bot_config(self, bot):
        botdict = {
            "roi": int(bot.roi),
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
            "trades": int(len(bot.completedOrders))
        }
        # "pricesource": EnumPriceSource(bot.priceMarket.priceSource).name,
        # "primarycoin": bot.priceMarket.primaryCurrency,
        # "secondarycoin": bot.priceMarket.secondaryCurrency,
        df = pd.DataFrame.from_dict([botdict])

        return df

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
        ranges['macdslow'] = list(range(40, 80, 2))
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

            completedOrders = [{'orderId': None, 'orderStatus': None, 'orderType': None, 'price': None,
                                'amount': None, 'amountFilled': None, 'unixTimeStamp': datetime.datetime.today().year()}for x in range(1)]
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
                            bot = self.bt_mh_on_update(x[1], ticks)
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

        bt = self.c.customBotApi.backtest_custom_bot(
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
    def return_bot(self, guid):
        bot = self.c.customBotApi.get_custom_bot(
            guid, EnumCustomBotType.MAD_HATTER_BOT).result
        return bot


class ScalperBotClass(Bot):
    def __init__(self):
        Bot.__init__(self)
        self.ticks = Haas().read_ticks()

    def return_scalper_bots(self):

        bl = self.c.customBotApi.get_all_custom_bots().result
        botlist = [x for x in bl if x.botType == 3]
        return botlist

    def bot_selector(self):
        bots = self.return_scalper_bots()
        b2 = [(f'{i.name} {i.priceMarket.primaryCurrency}-{i.priceMarket.secondaryCurrency}, {i.roi}', i)
              for i in bots]
        question = [inquirer.Checkbox(
            'bots', message='Select one or more bots using spacebar and then press return', choices=b2)]
        selection = inquirer.prompt(question)
        try:
            self.bot = selection['bots']
        except TypeError:
            print('No bot has been selected, you must select one')
            self.bot_selector()
        return selection['bots']

    def markets_selector(self):

        markets = self.c.marketDataApi.get_all_price_markets().result
        m2 = [(f'{EnumPriceSource(i.priceSource).name},{i.primaryCurrency}-{i.secondaryCurrency}', i)
              for i in markets]

        question = [inquirer.Checkbox(
            'markets', message="Select markets", choices=m2)]

        selection = inquirer.prompt(question)
        self.markets = selection['markets']
        # print(selection)
        return selection

    def setup_scalper_bot(self, bot, targetpercentage, safetythreshold):

        do = self.c.customBotApi.setup_scalper_bot(accountguid=bot.accountId, botguid=bot.guid, botname=bot.name, primarycoin=bot.priceMarket.primaryCurrency, secondarycoin=bot.priceMarket.secondaryCurrency, templateguid=bot.customTemplate,
                                                   contractname=bot.priceMarket.contractName, leverage=bot.leverage, amountType=bot.amountType, tradeamount=1000, position=bot.coinPosition, fee=bot.currentFeePercentage, targetpercentage=targetpercentage, safetythreshold=safetythreshold)
        print('result: ', do.errorCode, do.errorMessage)
        return do.result

    def set_targetpercentage_range(self):
        start_input = [inquirer.Text(
            'start', message='Define start of the target percentage range', default=0.5)]
        end_input = [inquirer.Text(
            'end', message='Define end of the target percentage range', default=1.5)]
        step_input = [inquirer.Text(
            'step', message='Define number of steps between start and end', default=0.2)]

        start = inquirer.prompt(start_input)['start']
        end = inquirer.prompt(end_input)['end']
        step = inquirer.prompt(step_input)['step']
        self.targetpercentage = [start, end, step]

    def set_safetythreshold_range(self):
        start_input = [inquirer.Text(
            'start', message='Define start of the safety threshold range', default=1)]
        end_input = [inquirer.Text(
            'end', message='Define end of the safety threshold range', default=5)]
        step_input = [inquirer.Text(
            'step', message='Define number of steps between start and end', default=0.2)]

        start = inquirer.prompt(start_input)['start']
        end = inquirer.prompt(end_input)['end']
        step = inquirer.prompt(step_input)['step']
        self.safetythreshold = [start, end, step]
    
    def bt_date_to_unix(self):
            c = Haas().read_cfg()
            min = c['BT DATE'].get('min')
            hour = c['BT DATE'].get('hour')
            day = c['BT DATE'].get('day')
            month = c['BT DATE'].get('month')
            year = c['BT DATE'].get('year')
            btd = datetime.datetime(int(year), int(month), int(day), int(hour), int(min))
            return btd

    def backtest(self):
        btd = self.bt_date_to_unix()
        if len(self.bot) > 0:
            with alive_bar(len(self.bot)) as bar:
                for bot in self.bot:
                    if len(bot.completedOrders)>0:
                        if bot.completedOrders[-1].unixAddedTime>btd.timestamp():
                            pass
                    else:
                    
                        results = []
                        columns = ['roi', 'safetythreshold', 'targetpercentage']

                        for s in tqdm(np.arange(float(self.safetythreshold[0]), float(self.safetythreshold[1]), float(self.safetythreshold[2]))):

                            for t in tqdm(np.arange(float(self.targetpercentage[0]), float(self.targetpercentage[1]), float(self.targetpercentage[2]))):

                                self.setup_scalper_bot(bot, targetpercentage=round(
                                    t, 2), safetythreshold=round(s, 2))

                                bt_result = self.c.customBotApi.backtest_custom_bot(
                                    bot.guid, self.ticks)
                                bt_result = bt_result.result
                                try:
                                    print('ROI: ', bt_result.roi, round(t, 2))
                                    total_results = {'roi': bt_result.roi, 'targetpercentage': round(
                                    t, 2), 'safetythreshold': round(s, 2)}

                                # results.append(total_results)
                                    results.append(
                                        [bt_result.roi, round(t, 2), round(s, 2)])
                                except:
                                    pass
                                df_res = pd.DataFrame(
                                    results, columns=columns, index=range(len(results)))
                                df_res.sort_values(by='roi', ascending=False, inplace=True)
                                df_res.reset_index(inplace=True, drop=True)
                                # print(df_res)
                                self.setup_scalper_bot(
                                    bot, df_res.safetythreshold.iloc[0], df_res.targetpercentage.iloc[0])
                                self.c.customBotApi.backtest_custom_bot(
                                    bot.guid, self.ticks)

        else:
            self.bot_selector()

    def scalper_bot_menu(self):
        # choices =
        menu = [inquirer.List('response', message='Please chose an action:', choices=[
                              'Select bots', 'Set range for safety threshold', 'Set range for target percentage', 'Backtest','backtest every bot', 'Main menu'])]

        while True:
            user_response = inquirer.prompt(menu)['response']
            if user_response == 'Select bots':
                self.bot_selector()
            elif user_response == 'Set range for safety threshold':
                self.set_safetythreshold_range()
            elif user_response == 'Set range for target percentage':
                self.set_targetpercentage_range()
            elif user_response == 'Backtest':
                self.backtest()
            elif user_response == 'backtest every bot':
                sb = ScalperBotClass()
                sb.bot = self.c.customBotApi.get_all_custom_bots().result
                sb.targetpercentage = [0.5,5,0.2]
                sb.safetythreshold = [1,2,0.2]
                sb.backtest()
            elif user_response == 'Main menu':
                break


class TradeBot(Bot):

    def __init__(self):
        Bot.__init__(self)

    def return_bot(self, guid):
        bot = self.c.tradeBotApi.get_trade_bot(guid).result
        return bot

    def get_indicators(self, bot):
        '''
        returns all tradebot indicators as a list
        '''

        idd = list([bot.indicators[x] for x in bot.indicators])
        return idd

    def select_indicator(self, indicators):

        for i, b in enumerate(indicators):
            print(i, indicators[i].indicatorTypeFullName)
        uip = input('Select indicator')

        indicator = indicators[int(uip)]
        print('select indicator', indicator)
        return indicator

    def setup_indicator(self, bot, indicator):
        setup = self.c.TradeBotApi.setup_indicator(bot.guid, indicator.guid,
                                                   bot.priceMarket, bot.priceMarket.primaryCurrency, bot.priceMarket.secondaryCurrency, bot.priceMarket.contractName, indicator.timer, indicator.chartType, indicator.deviation)
        print(
            f'Indicator setup was a {setup.errorCode.value}, {setup.errorMessage.value}')

    def get_interfaces(self, bot, indicator):

        interfaces = []
        for interface in bot.indicators[indicator.guid].indicatorInterface:
            interfaces.append({'title': interface.title, 'value': interface.value,
                               'options': interface.options, 'step': interface.step})

        return interfaces

    def get_full_interfaces(self, bot, indicator):
        interfaces = {}
        for interface in bot.indicators[indicator.guid].indicatorInterface:
            interfaces[EnumIndicator(
                bot.indicators[indicator.guid].indicatorType).name] = self.dict_from_class(interface)

        return interfaces

    def get_enums_for_indicators(self, bot):
        icc = ic()
        indicators_enums = {}
        for indicator in bot.indicators:
            indicator_enum = icc().get_indicator_enum_data(
                bot.indicators[indicator].indicatorInterface.indicatorType)
            indicators.append(indicator_enum)
        return indicators_enums

        return indicators

    def add_indicator(self, bot, indicator):
        failed = []
        try:
            add = self.c.tradeBotApi.add_indicator(bot.guid, indicator)
            if add.result:
                print('Indicator', EnumIndicator(
                    indicator).name, ' added to ', bot.name)
            else:
                print('Adding indicator didn\'t work out')

        except:
            failed.append(indicator)
        return failed

    def edit_indicator(self, bot, indicator, field, value):
        print(indicator)
        indicator_config = self.c.tradeBotApi.edit_bot_indicator_settings(
            bot.guid, indicator.guid, field, value)
        interfaces = self.get_interfaces(bot, indicator)
        return indicator_config

    def remove_indicator(self, bot, indicator):
        failed = []
        try:
            add = self.c.tradeBotApi.remove_indicator(bot.guid, indicator.guid)
            if add.result:
                print('Indicator', EnumIndicator(
                    indicator).value, ' removed from ', bot.name)
            else:
                print('Removing indicator didn\'t work out')

        except:
            failed.append(indicator)
        return failed

    def remove_indicators(self, bot, indicator_list):
        for x in indicator_list:
            self.remove_indicator(bot, x)

    def add_multiple_indicators(self, bot, indicators):
        for x in indicators:
            self.add_indicator(bot, x)

    def add_all_indicators(self, bot):
        indicators = [x for x in range(71)]
        self.add_multiple_indicators(bot, indicators)

    def remove_all_indicators(self, bot):
        indicators = t.get_indicators(bot)
        self.remove_indicators(bot, indicators)

    def select_bot_get_indicator(self, bot):
        indicators = self.get_indicators(bot)
        indicator = self.select_indicator(indicators)
        return indicator


class MarketData(Haas):
    def __init__(self):
        Haas.__init__(self)


    def to_df_for_ta(self, market_history):
        '''
        Transforms List of Haas MarketData into Dataframe
        '''
        market_data = [
            {

                "Date": x.unixTimeStamp,
                "Open": x.open,
                "High": x.highValue,
                "Low": x.lowValue,
                "Close": x.close,
                "Buy": x.currentBuyValue,
                "Sell": x.currentSellValue,
                "Volume": x.volume,
            }
            for x in market_history
        ]
        print(market_data)
        df = pd.DataFrame(market_data)

        try:
            df['Date'] = pd.to_datetime(df['Date'], unit='s')

        except:
            print('Whops')
            # print(df)
        return df

    def get_all_markets(self):
        '''
        Returns dataframe with "primarycurrency", "secondarycurrency",'pricesource','marketobj','Ticker'
        Ticker is primarycurrency, secondarycurrency in one word
        '''
        markets = [
            (

                i.primaryCurrency,
                i.secondaryCurrency,
                i.priceSource,
                i

            )
            for i in self.c.marketDataApi.get_all_price_markets().result
        ]
        df = pd.DataFrame(
            markets,
            columns=(["primarycurrency",
                      "secondarycurrency", 'pricesource', 'marketobj']))
        df.drop_duplicates(inplace=True, ignore_index=True)
        df['Ticker'] = df.primarycurrency.values+df.secondarycurrency.values
        return df

    def return_priceMarket_object(self, pricesource: EnumPriceSource, primarycoin=None, secondarycoin=None, ticker=None):
        '''
            Works in one of two ways: 
            1. pricesource,primarycoin,secondarycoin = marketobject
            2. pricesource, ticker = marketobject
        '''

        df = self.get_all_markets()

        if ticker != None:
            marketobj = df[df['Ticker'] == ticker][df['pricesource']
                                                   == pricesource].marketobj.values[0]
            return marketobj
        else:
            marketobj = df[df["pricesource"] == pricesource][df["primarycurrency"]
                                                             == primarycoin][df["secondarycurrency"] == secondarycoin].marketobj.values[0]
            return marketobj

    # @sleep_and_retry
    # @limits(calls=5, period=15)
    def get_market_data(self, priceMarketObject, interval, depth):
        '''
        Returns dataframe full of candlestick data including volume in any interval and depth supported by Haasonline.

        '''
        marketdata = self.c.marketDataApi.get_history_from_market(
            priceMarketObject, interval, depth)
        print('get_market_data', 'errorcode', marketdata.errorCode,
              'errormessage', marketdata.errorMessage)
        if marketdata.errorCode == EnumErrorCode.SUCCESS:

            if type(marketdata.result) == list:
                if len(marketdata.result) > 0:
                    df = self.to_df_for_ta(marketdata.result)
                    return df
                else:
                    time.sleep(5)
                    return self.get_market_data(priceMarketObject, interval, depth)
            else:
                time.sleep(10)
                return self.get_market_data(priceMarketObject, interval, depth)
        else:
            time.sleep(10)
            return self.get_market_data(priceMarketObject, interval, depth)


    def save_market_data_to_csv(self, marketData, marketobj):
        '''
        Saves provided MarketData dataframe to CSV file in a name format provided below
        '''
        filename = f'{EnumPriceSource(marketobj.priceSource).name}-{marketobj.primaryCurrency}-{marketobj.secondaryCurrency}-{len(marketData)}.csv'
        if len(marketData) > 0:
            marketData.to_csv(f'./market_data/{filename}')
            print(f'{EnumPriceSource(marketobj.priceSource).name} | {marketobj.primaryCurrency} | {marketobj.secondaryCurrency} sucessfuly saved to csv')
            return f"sucessfully saved {filename} to market_data folder, with {len(marketData)} ticks included"
        else:
            return f"Market Data is empty. {filename} has not been saved."

    def read_csv(self, file, nrows=None):
        '''
        Reads MarketData csv file into a dataframe
        '''
        data = BotDB().read_csv(file, nrows=nrows)
        def uppercase(x): return str(x).capitalize()
        data.rename(uppercase, axis='columns', inplace=True)
        data['Data'] = pd.to_datetime(data['Data'])
        dti = pd.DatetimeIndex([x for x in data['Date']])
        data.set_index(dti, inplace=True)
        print(data)
        return data

        """
        Below are DASH recepies for market related data
        """

class HaasDash(MarketData):

    def __init__(self):
        MarketData.__init__(self)

    def markets_dropdown(self):

        markets = self.get_all_markets()
        markets_dropdown = [{'label': str(x), 'value': str(
            x)} for x in markets.pricesource.unique()]
        return markets_dropdown

    def primarycoin_dropdown(self, pricesource):

        df = self.get_all_markets()
        pairs = df[df["pricesource"] == pricesource]

        return pairs.primarycurrency.unique()

    def secondary_coin_dropdown(self, pricesource, primarycurrency):

        df = self.get_all_markets()
        df = self.get_all_markets()
        pairs = df[df["pricesource"] ==
                   pricesource][df['primarycurrency'] == primarycurrency]
        return pairs.secondarycurrency.unique()



class InteractiveBT(Bot):
    def __init__(self):
        Bot.__init__(self)
        self.indicator_vars = ['guid', 'RsiLength', 'RsiOversold', 'RsiOverbought', 'MacdFast', 'MacdSlow', 'MacdSign',
                               'Length', 'Devup', 'Devdn', 'MaType', 'Deviation', 'ResetMid', 'AllowMidSell', 'RequireFcc', 'Interval']
        self.indicators = ['rsi', 'bBands', 'macd']
        self.interval = ['Interval', 'interval']
        self.ticks = Haas().read_ticks()
        # self.B =  BotDB()

    @sleep_and_retry
    @limits(calls=2, period=1)
    def return_botlist(self):

        bl = self.c.customBotApi.get_all_custom_bots().result
        botlist = [x for x in bl if x.botType == 15]
        # print(botlist)
        return botlist

    def identify_bot(self, botlist):
        self.print_user_message()
        while True:
            botlist2 = self.return_botlist()

            lists = zip(botlist, botlist2)
            for x in lists:
                c = self.compare_indicators(x[0], x[1])
                try:
                    if len(c) != 0:
                        # print('x1', x[1].name)
                        return x[1]
                        break

                    else:
                        self.identify_bot(botlist)
                except:
                    pass

    @sleep_and_retry
    @limits(calls=2, period=1)
    def monitor_bot(self, bot):
        botlist = self.return_botlist()

        for bot2 in botlist:
            if bot.guid == bot2.guid:
                bot2 = bot2

        try:
            c = self.compare_indicators(bot, bot2)
        except Exception as e:
            print(e)
        try:
            if len(c) != 0:
                bt = self.bt_mh_on_update(bot)
                os.system('clear')

                return bt
        except:
            pass

        else:
            bt = self.monitor_bot(bot)

    def compare_indicators(self, bot, bot2):
        indicators = []
        important_indicators = []
        for b in [bot, bot2]:
            important_indicators.append(('Interval:', b.interval))
            for i in ['rsi', 'bBands', 'macd']:
                try:
                    indicators.append((i, b.__dict__[i]))
                except Exception as e:
                    # print('exception at compare', e)
                    indicators.append((i, b.__dict__[i].__dict__))

        for i in indicators:
            for ii in i:
                for v in ['RsiLength', 'RsiOversold', 'RsiOverbought', 'MacdFast', 'MacdSlow', 'MacdSign', 'Length', 'Devup', 'Devdn', 'MaType', 'Deviation', 'ResetMid', 'AllowMidSell', 'RequireFcc', 'Interval']:
                    try:
                        important_indicators.append((v, ii[v]))

                    except Exception as e:
                        # print('Exception on specific indicator params',e)
                        pass

                    try:
                        important_indicators.append((v, ii.__dict__[v]))
                        # print('try on the exception',v,ii.__dict__[v])
                    except Exception as e:
                        # print('indcators in compare indicator',e,v)
                        pass

        from collections import defaultdict
        d = defaultdict(tuple)
        for tup in important_indicators:
            d[tup[0]] += (tup[1])

        with_diff = defaultdict(tuple)
        try:
            for tup in d:
                # print()
                try:
                    diff = d[tup][0]-d[tup][1]
                except:
                    diff = 0
                if diff != 0:
                    with_diff[tup] = diff

        except Exception as e:
            print(e)

        if len(with_diff) != 0:
            return [(i, d[i], with_diff[i]) for i in d]

    @sleep_and_retry
    @limits(calls=2, period=1)
    def bt_mh_on_update(self, bot):

        bt = self.c.customBotApi.backtest_custom_bot(bot.guid, self.ticks)
        try:
            bot = MadHatterBot().return_bot(bt.result.guid)
        except:
            bot = MadHatterBot().return_bot(bot.guid)

        if bt.errorCode != EnumErrorCode.SUCCESS:
            os.system('clear')
            print("bt", bt.errorCode, bt.errorMessage)

            self.bt_mh_on_update(bot)

        else:
            print(bt.errorCode, bt.errorMessage, 'else')
            return bt.result

    def backtest(self, loop_count=1):
        def to_df(sat):
            df = pd.DataFrame(sat)
            df.reset_index()

            dfs = []
            for i in sat:
                config = MadHatterBot().bot_config(i)
                dfs.append(config)

            configs = pd.concat(dfs)
            configs.drop_duplicates()
            filename = str(bot.name.replace('/', '_'))+str("_")+str(datetime.date.today().month) + \
                str('-')+str(datetime.date.today().day) + \
                str("_")+str(len(configs))+str('.csv')

            configs.to_csv(filename)
            # print(f'Results are saved to {filename}.csv')
            # df.to_json(f'{filename}.json')
            return configs
        sat = []

        botlist = self.return_botlist()
        bot = self.identify_bot(botlist)

        sat.append(bot)
        loops = []
        # loop_count = 10

        while True:
            try:
                bot2 = self.monitor_bot(bot)
            except (KeyboardInterrupt, SystemExit):
                print('Stopping and saving')
                df = to_df(sat)
            try:
                if sat[-1].roi != bot2.roi:
                    sat.append(bot2)
                    loops = 0
                else:
                    if sat[-1].roi == bot2.roi:
                        loops += 1
            except Exception as e:
                continue
            print('Current ROI: ', bot2.roi, 'Best ROI:', sorted(
                sat, key=lambda x: x.roi, reverse=True)[0].roi)
            print('SAME_ROI Loop Count: ', loops)
            print('AutoBT will stop on SAME_ROI Loop Count: ', loop_count)
            print('Best Config: ')
            best_config = MadHatterBot().bot_config(sorted(
                sat, key=lambda x: x.roi, reverse=True)[0])
            print(best_config)
            if loops == int(loop_count):
                df = to_df(sat)
                break

    def load_results(self):

        files = self.B.get_csv_files()
        file = self.B.select_from_list(files)
        db = self.B.read_csv(file)
        # print(db)
        return db

    def apply_config(self, bot, template):
        B = BotDB()
        try:
            print('Applying bot configuration...')
            result = B.setup_bot_from_obj(bot, template)
            print('Config from *.json file detected')

        except Exception:
            print('Config from *.csv file detected')
            result = B.setup_bot_from_csv(bot, template)
        else:
            print('Bot has not been configured due to some Error')
        return result

    def print_user_message(self):

        print("")
        print('InteractiveBT, or AssistedBT implies that you are manually changing bot parameters while backtesting is triggered automatically at a given interval or by a bot parameter change')
        print('Every BT session, is saved on your drive. Session ends if the ROI of the last 10 backtests was exactly the same. Every config from it can be applied to any other MH bot afterwards')
        print('Open any Mad-Hatter bot in FULL SCREEN, open BOT REMOTE to instantly see backtestin results, navigate to indicators tab, click on any parameter value. Now, with keyaboard arrow keys change the value up and down.')
        print('TAB and SHIFT+TAB keys, provide you with immense speed of indicators navigation!')
        print('As long as typing coursor able to edit indicator values now, pressing TAB will move it to the next numeric parameter above. SHIFT+TAB moves it down.')
        print('Parameters with options like MA type are skipped.')
        print(
            'bBands deviations have to be changed by quickly writing values down by numbers')
        print('To begin the process, simply chose Mad-Hatter Bot and change a few params here and there with the above written method!')
        print('Waiting for any MH bot parameter to change')


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

    def get_csv_files(self, path='./'):
        files = []
        for file in os.listdir(path):
            # if file.endswith(".csv") or file.endswith('.json'):
            if file.endswith(".csv"):
                files.append(os.path.join(path, file))
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
                print('csv', e)
            return configs
        else:
            return 'csv was not read'

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
                config['rsis'])

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
                config.rsi['RsiOversold'])

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
                mappedSellSignal=bot.mappedSellSignal).result

        print(bot.name, ' Has been configured')
        # Indicator parameters have been set

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
                mappedSellSignal=bot.mappedSellSignal).result

        print(bot.name, ' Has been configured')

    # @lru_cache(maxsize=None)
    def bt_bot(self, bot, depth):
        bt = self.c.customBotApi.backtest_custom_bot(

            bot.guid,
            depth)

        # print(btres.roi)
        return bt.result

    def iterate_csv(self, configs, bot, depth):
        best_roi = 0
        configs.roi[0:-1] = 0
        cols = ['interval', 'signalconsensus', 'fcc', 'resetmiddle',
                'allowmidsells', 'matype', 'rsil', 'rsib', 'rsis', 'bbl', 'devup',
                'devdn', 'macdfast', 'macdslow', 'macdsign', 'trades', 'roi']
        for c in configs.columns:
            if c not in cols:
                configs.drop(c, axis=1, inplace=True)
        markets = self.c.marketDataApi.get_price_markets(
            bot.priceMarket.priceSource).result
        for market in markets:
            if market.primaryCurrency == bot.priceMarket.primaryCurrency:
                if market.secondaryCurrency == bot.priceMarket.secondaryCurrency:
                    if bot.currentTradeAmount < market.minimumTradeAmount:
                        bot.currentTradeAmount = 10000
        with alive_bar(len(configs.index), title=f"{bot.name} backtesting. ") as bar:

            for i in configs.index:

                print('Current Backtest ROI: ', bt.roi,
                      '%', 'best ROI:', best_roi, '%')
                print('\nTop 5 configs so far:\n')
                print(configs.sort_values(by='roi', ascending=False)[0:5])

                config = configs.iloc[i]
                s = self.setup_bot_from_csv(bot, config)
                try:
                    print(s.errorCode)
                except Exception as e:
                    print(e)
                bt = self.c.customBotApi.backtest_custom_bot_on_market(
                    bot.accountId,
                    bot.guid,
                    int(depth),
                    bot.priceMarket.primaryCurrency,
                    bot.priceMarket.secondaryCurrency,
                    bot.priceMarket.contractName).result
                try:
                    print(bt.errorCode)
                except Exception as e:
                    print(e)
                if bt.roi > best_roi:
                    best_roi = bt.roi
                configs['roi'][i] = bt.roi

                bar()

        return configs

    def verify_cfg(self):
        c = ConfigParser


def time_limited_test_menu():
    if datetime.date.today() < datetime.date(2020, 8, 24):
        test_menu()
    else:
        print('Trial has ended. Contact Cosmos directly via twitter or discord for more.')
        time.sleep(120)
        print('Exiting ...')
        time.sleep(5)


def test_menu():
    M = Main_Menu()
    a = M.main_screen()


def scalper_test_menu():
    # sc = ScalperBotClass().return_scalper_bots()
    # print(sc)
    s = ScalperBotClass()
    bots = s.scalper_bot_menu()

    # ms = ScalperBotClass().markets_selector()
if __name__ == "__main__":
    # main()
    test_menu()
