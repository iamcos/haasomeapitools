import datetime
import os
from functools import lru_cache
from BaseHaas import Bot
import dateutil.relativedelta
import ipywidgets as widgets
import pandas as pd
from haasomeapi.enums.EnumMadHatterIndicators import EnumMadHatterIndicators
from haasomeapi.enums.EnumMadHatterSafeties import EnumMadHatterSafeties
from haasomeapi.HaasomeClient import HaasomeClient
from ipywidgets import interact
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from ratelimit import limits, sleep_and_retry
import configserver
from botsellector import BotSellector
import streamlit as st

from deepdiff import DeepDiff

class InteractiveBT(Bot):
    def __init__(self):
        Bot.__init__(self)

    @sleep_and_retry
    @limits(calls=3, period=2)
    def return_tradebot_list(self):
        bl = self.c().tradeBotApi.get_all_trade_bots().result
        return bl


    def return_edited_bot(self):
        botlist = self.return_tradebot_list()
        while True:
            botlist2 = self.return_tradebot_list()
            lists = zip(botlist,botlist2)
            for x in lists:
                c= self.compare_indicators(x[0],x[1])
                if c == False:
                    return x[1]
    @sleep_and_retry
    @limits(calls=4, period=3)
    def monitor_bot(self,bot, ticks):
        botlist = self.return_tradebot_list()
        for b in botlist:
            if b.guid == bot.guid:
                c = self.compare_indicators(bot,b)
                if c == True:
                    pass
                elif c == False:
                    bot = self.bt_tb_on_update(b, ticks)
                return bot

    def compare_indicators(self, bot, bot1):
            # print(bot.rsi, '\n',bot1.rsi)
        diff = DeepDiff(bot,bot1, verbose_level=1,view='tree')

        if len(diff) > 0:
            print(diff)

            return False
        elif len(diff) == 0:
            return True

    @sleep_and_retry
    @limits(calls=3, period=2)
    def bt_tb_on_update(self, bot, ticks):

        bt = self.c().tradeBotApi.backtest_trade_bot(
            bot.guid,
            int(ticks)
        )
        if bt.errorCode != EnumErrorCode.SUCCESS:
            st.write("bt", bt.errorCode, bt.errorMessage)
        else:
            # print(bt.result.roi)
            # print(bt.errorCode, bt.errorMessage)
            return bt.result
    def interactiveBT(self,depth):
        st.title('Trade Bot AutoBacktesting script')
        st.write('This script, when run live automatically detect a bot who\'s config have been updated most recently and continues onward with it.')
        bot = self.return_edited_bot()
        results = []
        while True:
            bot = self.monitor_bot(bot, depth)
            results.append(bot)
            if bot.name.startswith('STOP'):
                return results
        results
if __name__ == "__main__":
    results = InteractiveBT().interactiveBT(1400)
