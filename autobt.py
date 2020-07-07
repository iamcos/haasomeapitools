import configparser as cp
import csv
import datetime
import os
import re
import time
from functools import lru_cache
from deepdiff import DeepDiff
from haasomeapi.enums.EnumCustomBotType import EnumCustomBotType
import click
import pandas as pd
import six
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from haasomeapi.enums.EnumMadHatterIndicators import EnumMadHatterIndicators
from haasomeapi.enums.EnumMadHatterSafeties import EnumMadHatterSafeties
from haasomeapi.HaasomeClient import HaasomeClient
from ratelimit import limits, sleep_and_retry

# import configserver
import sendgrid
from BaseHaas import Bot, Haas, MadHatterBot
from botdb import BotDB
from botsellector import BotSellector
from pyconfigstore import ConfigStore
from pyfiglet import figlet_format
from PyInquirer import (Token, ValidationError, Validator, print_json, prompt,
            style_from_dict)
from sendgrid.helpers.mail import *

try:
  import colorama
  colorama.init()
except ImportError:
  colorama = None

try:
  from termcolor import colored
except ImportError:
  colored = None
from examples import custom_style_2

style = style_from_dict({
  Token.QuestionMark: '#E91E63 bold',
  Token.Selected: '#673AB7 bold',
  Token.Instruction: '',  # default
  Token.Answer: '#2196f3 bold',
  Token.Question: '',
  })


def read_ticks():
  config = configparser.ConfigParser()
  try:
    with open('config.ini', 'r') as configfile:
      min, hour, day, month, year = config.read(configfile)['BT DATE']

      bt_date = datetime.datetime(year, month, day, hour, minute)
      return bt_date
  except:
    print(f'Unable to read Backtesting start date. Lets set it.')

    start_datetime = [
      {
        'ty'
      }
    ]


# hello()

def calculate_ticks(start_date, end_date):
  diff = end_date-start_date
  secs = diff.total_seconds()/60
  return int(secs)


bots = BotDB().get_mh_bots()

files = BotDB().get_csv_files()
# filessellector = widgets.Dropdown(options=[x for x in files],value=files[2],description='Config file',disabled=False,)
# start_date=
end_date = datetime.date.today()
bd = BotDB()
'''

'''
# display(botsellector), display(filessellector)
ticks = Haas().read_ticks()
'''

'''
bd = BotDB()
# configs = bd.read_csv(filessellector.value)
# results = bd.iterate_csv(configs, botsellector.value, ticks)
# print('Backtesting Stage Complete')

'''
'''
# Run this cell as well. It performs sorting and cleaning operations on the results from above.
# Here will also be an error printed. Ignore that too.

# results.sort_values(by='roi', ascending=False, inplace=True)
# cols = results.columns.tolist()
# # print(cols)
# cols = ['roi','interval', 'signalconsensus',
#         'fcc', 'resetmiddle', 'allowmidsells',
#         'matype', 'rsil', 'rsib', 'rsis', 'bbl',
#         'devup', 'devdn', 'macdfast', 'macdslow',
#         'macdsign', 'trades']
# results.reset_index()
# results = results[cols]


# This cell displays results in a more meaningful table-fashion manner for you to analyze.
# You have an ability to select how many configurations are displayed in dropdown above the table.
# In general you only need to care for the first row and Roi row.
# In the first row is bot configuration number. Roi is backtesting results
# To apply a bot configuration to the selected bot, type its number Below the table and click
# "Apply config" button for the bot to be configured according and backtested for you to see.
# Once applied, go to Haas interface, select that bot one more time by mouseclicking it
# if not in full screen, to see changes to its configuration.
# You should see the configuraion backtesting results, trades and so on once backtest is complete.
# There is no limit to he number of configurations you can apply to your bot, so take your time
# To analyzer the best ones in Bot Analyzer in Haas interface to make sure that it's trades align
# with your expectations before going to the next stage.
# Once this cell run, you may have to scroll up a bit to see the table, so make sure to do that
# its not at sight.
# Backtesting results may slightly vary from what is in the table, usually by not much.

# results.reset_index()
# try:
#     results.drop(['Unnamed: 0', ],axis=1,inplace=True)
# except:
#     pass
# opt.lengthMenu = [10, 20, 50, 100]
# show(results)
# results_sellector = widgets.Dropdown(
#     options= [x for x in results.index],
#     value=results.index[0],
#     description='Botlist',
#     disabled=False,
# )
def configure_bot_from_csv_by_id(index):
    bot = botsellector.value

    config = configs.loc[index]
    bd.setup_bot_from_csv(bot, config)
    bt = bd.bt_bot(bot, int(ticks))


# button = widgets.Button(description="Apply config")
# output = widgets.Output()
# r_s = widgets.IntText(
#     value=0,
#     min=0,
#     step=1,
#     description='Bot Num:',
#     disabled=False
# )
# display(r_s,button,output)


class InteractiveBT(Bot):
  def __init__(self):
    Bot.__init__(self)

  @sleep_and_retry
  @limits(calls=2, period=1)
  def return_botlist(self):

    bl = self.c.customBotApi.get_all_custom_bots().result
    botlist = [x for x in bl if x.botType == 15]
    # print(botlist)
    return botlist

  def identify_bot(self,botlist):
    while True:
      botlist2 = self.return_botlist()
  

      lists = zip(botlist, botlist2)
      for x in lists:
        c = self.compare_indicators(x[0], x[1])

        if len(c)!=0:
          print('x1', x[1].name)
          return x[1]
          break
          
        else:
            self.identify_bot(botlist)


  @sleep_and_retry
  @limits(calls=2, period=1)
  def monitor_bot(self, bot, ticks):
      botlist = self.return_botlist()
      
      for bot2 in botlist:
            if bot.guid == bot2.guid:
                  bot2 = bot2
        
      try:
        c = self.compare_indicators(bot, bot2)
      except Exception as e:
        print(e)
     
      if len(c) !=0:
          print('indicators monitoring',len(c))
          bt = self.bt_mh_on_update(bot, ticks)
          # e = MadHatterBot().return_bot(d.guid)
          print(bt.roi)
        
          return bt
          
      else:
            bot = bot
            ticks = ticks

            self.monitor_bot(bot,ticks)

  def compare_indicators(self, bot, bot2):
    indicators = []
    important_indicators = []
    for b in [bot, bot2]:
        important_indicators.append(('Interval:', b.interval))
        for i in ['rsi', 'bBands', 'macd']:
              try:
                indicators.append((i, b.__dict__[i]))
              except Exception as e:
                print('exception at compare', e)
                indicators.append((i, b.__dict__[i].__dict__))

    for i in indicators:
      for ii in i:
          for v in ['RsiLength', 'RsiOversold', 'RsiOverbought', 'MacdFast', 'MacdSlow', 'MacdSign','Length', 'Devup', 'Devdn', 'MaType', 'Deviation', 'ResetMid', 'AllowMidSell', 'RequireFcc', 'Interval']:
            try:
                important_indicators.append((v, ii[v]))

            except Exception as e:
              # print('Exception on specific indicator params',e)
              pass
              
            try:
                  important_indicators.append((v, ii.__dict__[v]))
                  print('try on the exception',v,ii.__dict__[v])
            except Exception as e:
                  # print('indcators in compare indicator',e,v)
                 pass

    from collections import defaultdict
    d=defaultdict(tuple)
    for tup in important_indicators:
         d[tup[0]] += (tup[1],)

    with_diff= defaultdict(tuple)
    try:
      for tup in d:
            # print()
            try:
              diff = d[tup][0]-d[tup][1]
            except:
              diff = 0
            if diff !=0:
              with_diff[tup] = diff

    except IndexError as e:
      
      print('compare indicators, with diff',e,tup,d[tup],d[tup][0:-1])
    except Exception as e:
      print(e)

    for i in with_diff:
          print(i,d[i],with_diff[i])
          print('len of diff',len(with_diff))
    if len(with_diff) !=0:
          
      return [(i,d[i],with_diff[i]) for i in d]
    elif len(with_diff) == 0:
          return []




  @ sleep_and_retry
  @ limits(calls=2, period=1)
  def bt_mh_on_update(self, bot, ticks):

    bt=self.c.customBotApi.backtest_custom_bot(bot.guid,int(ticks))
    bot = MadHatterBot().return_bot(bt.result.guid)
   
    
    while bt.errorMessage != EnumErrorCode.SUCCESS:
      print("bt", bt.errorCode.value, bt.errorMessage.value)
      # print('sleeping for a few secs')
      # time.sleep(1)
      self.bt_mh_on_update(bot,ticks)
      # print(bt.result.roi)
      # print(bt.errorCode, bt.errorMessage)
    else:
      print(bt.errorCode, bt.errorMessage)
      return bt.result




'''
'''
semi_auto_tuning=[]
ibt=InteractiveBT()
botlist = ibt.return_botlist()
bot=ibt.identify_bot(botlist)
print(bot.name, bot.roi)
indicators_changes = []
sat=semi_auto_tuning
sat.append(bot)

while True:
    print(sat[-1])
    bot2 = ibt.monitor_bot(sat[-1], ticks)
    sat.append(bot2)
    print('sat.bot',sat[-1])
    print('sat total', sat)
   

'''
'''

df=pd.DataFrame([{'ROI': b.roi, 'Bot': b} for b in semi_auto_tuning])
df.sort_values(by='ROI', ascending=False, inplace=True)
df.reset_index()
print(df)

def configure_bot_from_botobject(index):
    config=df.Bot.iloc[index]
    # print(config)
    bd.setup_bot(bot, config)
    bot=bd.bt_bot(bot, int(ticks))


# '''
# bot = bd.bt_bot(botsellector.value,1)
# setup = bd.setup_bot(bot,botsellector.value)

# '''
# '''

# '''
# '''

# '''
# '''
