import configparser as cp
import csv
import datetime
import os
import re
import time
from functools import lru_cache

import click
import pandas as pd
# import configserver
import sendgrid
import six
from deepdiff import \
    DeepDiff  # For finding if item exists in an object; For Deep Difference of 2 objects
from deepdiff import DeepHash  # For hashing objects based on their contents
from deepdiff import DeepSearch, grep
from examples import custom_style_2
from haasomeapi.enums.EnumCustomBotType import EnumCustomBotType
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from haasomeapi.enums.EnumMadHatterIndicators import EnumMadHatterIndicators
from haasomeapi.enums.EnumMadHatterSafeties import EnumMadHatterSafeties
from haasomeapi.HaasomeClient import HaasomeClient
from pyconfigstore import ConfigStore
from pyfiglet import figlet_format
from PyInquirer import (Token, ValidationError, Validator, print_json, prompt,
                        style_from_dict)
from ratelimit import limits, sleep_and_retry
from sendgrid.helpers.mail import *

from BaseHaas import Bot, Haas, MadHatterBot
from botdb import BotDB
from botsellector import BotSellector

try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None

try:
    from termcolor import colored
except ImportError:
    colored = None



class InteractiveBT(Bot):
    def __init__(self):
        Bot.__init__(self)
        self.indicator_vars = ['guid', 'RsiLength', 'RsiOversold', 'RsiOverbought', 'MacdFast', 'MacdSlow', 'MacdSign',
                               'Length', 'Devup', 'Devdn', 'MaType', 'Deviation', 'ResetMid', 'AllowMidSell', 'RequireFcc', 'Interval']
        self.indicators = ['rsi', 'bBands', 'macd']
        self.interval = ['Interval', 'interval']
        self.ticks =  Haas().read_ticks()
        self.B =  BotDB()

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

        if len(c) != 0:
            bt = self.bt_mh_on_update(bot)
            os.system('clear')

            return bt

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
            d[tup[0]] += (tup[1],)

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

    def backtest(self,loop_count =1):
        def to_df(sat):
            df = pd.DataFrame(sat)
            df.reset_index()
            filename = (bot.name.replace('/','_')
			+ str("_")
			+ str(datetime.date.today().month)
			+ str(datetime.date.today().day)
			+ str("_")
			+ str(len(sat)))
            dfs = []
            for i in sat:
                config = MadHatterBot().bot_config(i)
                dfs.append(config)
               
            configs = pd.concat(dfs)
            configs.drop_duplicates()
            configs.to_csv(f'{filename}.csv')
            # print(f'Results are saved to {filename}.csv')
            df.to_json(f'{filename}.json')
            return df
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
                print(e)
            print('Current ROI: ', bot2.roi, 'Best ROI:', sorted(
                sat, key=lambda x: x.roi, reverse=True)[0].roi)
            print('SAME_ROI Loop Count: ', loops)
            print('AutoBT will stop on SAME_ROI Loop Count: ', loop_count)
            print('Best Config: ')
            best_config =  MadHatterBot().bot_config(sorted(
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
        print('InteractiveBT implies that you are manually changing bot parameters while backtesting is triggered automatically at a given interval or by a bot parameter change')
        print('Every BT session, is saved on your drive. Session ends if the ROI of the last 10 backtests was exactly the same. Every config from it can be applied to any other MH bot afterwards')
        print('Open any Mad-Hatter bot in FULL SCREEN, open BOT REMOTE to instantly see backtestin results, navigate to indicators tab, click on any parameter value. Now, with keyaboard arrow keys change the value up and down.')
        print('TAB and SHIFT+TAB keys, provide you with immense speed of indicators navigation!') 
        print('As long as typing coursor able to edit indicator values now, pressing TAB will move it to the next numeric parameter above. SHIFT+TAB moves it down.')
        print('Parameters with options like MA type are skipped.')
        print('bBands deviations have to be changed by quickly writing values down by numbers')
        print('To begin the process, simply chose Mad-Hatter Bot and change a few params here and there with the above written method!')
        print('Waiting for any MH bot parameter to change')

if __name__ == '__main__':
      
    InteractiveBT().backtest()


#   rs = InteractiveBT().load_results()
#   print(rs[0][1:5].values)
