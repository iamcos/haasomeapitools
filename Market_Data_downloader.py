import time
import datetime
from math import pi
import streamlit as st
import pandas as pd
import numpy as np
from alive_progress import alive_bar
import plotly.figure_factory as ff
from BaseHaas import MarketData as md
from BaseHaas import Haas, BotDB, MadHatterBot, HaasDash
from haasomeapi.HaasomeClient import HaasomeClient
import dtale
import os
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models.widgets import Dropdown
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.plotting import figure, output_file, show
from ta import add_all_ta_features
from ta.utils import dropna
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st
from datetime import date
import datetime
import io
from bokeh.models import BooleanFilter, CDSView, Select, Range1d, HoverTool
from bokeh.palettes import Category20
from bokeh.models.formatters import NumeralTickFormatter
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from bokeh.models import CustomJS, ColumnDataSource, HoverTool, NumeralTickFormatter
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
from ratelimit import limits, sleep_and_retry
import configparser as cp
class StreamlitHaasTool:
    def __init__(self):
        self.md = md
        self.market = None
        self.depth = self.setup_bt
        self.interval = int(5)
        self.BotDB = BotDB
        self.bots = self.return_bots
        self.configs = self.return_configs
        self.num_configs = None
        self.MadHatterBot = MadHatterBot
        self.client = None

    def get_creds(self):
       
        write = st.sidebar.write('Haas Local API data')
        adr = st.sidebar.text_input('Server ip: ')
        port = st.sidebar.text_input('Server port:')
        secret = st.sidebar.text_input('API key/secret: ')

        ip = str('http://'+adr+':'+port)
        client = HaasomeClient(ip, secret)
        self.client = client
        self.md().c = client
        botdb = self.BotDB.c = client
        self.MadHatterBot.c = client
        self.client = client
     
        if self.md().c.test_credentials().errorCode == EnumErrorCode.SUCCESS:
                d =  st.write('LOGIN SUCCESSFULL')
                time.sleep(5)
                d = None
       


    def market_selector(self):
        hd = HaasDash()
        markets = self.md().get_all_markets()
        
        pricesource = st.sidebar.selectbox(
            'Select Exchange',
            (markets.pricesource.unique()), index=2)

        primarycurrency = st.sidebar.selectbox(
            'Primary coin', (hd.primarycoin_dropdown(pricesource)))
        secondarycurrency = st.sidebar.selectbox(
            'Secondary coin', (hd.secondary_coin_dropdown(pricesource, primarycurrency)))
        market_object = self.md().return_priceMarket_object(
            pricesource, primarycurrency, secondarycurrency)
        st.title(
            f'Haasonline market data dashboard. {pricesource},{primarycurrency},{secondarycurrency}')
        self.market = market_object
        return market_object
    # @st.cache
    def fetch_data(self):
        get = st.sidebar.button('Get Data')
        if get:
            data = self.get_data()
            get = False
            return data

    def get_data(self):
            data = self.md().get_market_data(self.market, self.interval, self.depth)
            return data
        
    def _max_width_(self):
        max_width_str = f"max-width: 3000px;"
        st.markdown(
            f"""
        <style>
        .reportview-container .main .block-container{{
            {max_width_str}
        }}
        </style>    
        """,
            unsafe_allow_html=True,
        )

    def setup_bt(self):
        date = st.sidebar.date_input('Select starting bt date',
                                    value=(datetime.date.today() - datetime.timedelta(days=1)))
        time = st.sidebar.time_input('Select starting time')
        dto = datetime.datetime.combine(date, time)
        today = datetime.datetime.today()
        diff = today-dto
        depth = int(diff.total_seconds()/60
        /int(self.interval))
        print('date ', date, 'time ', time, 'diff ',
            diff, 'depth ', depth, 'interval', self.interval)
        self.depth = depth
        
    def setup_candlesize(self):
        interval = st.sidebar.selectbox(
            'Candle size', ([1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 45, 60, 90, 120]),index=4)
        self.interval = interval
    def plot_market_data(self,marketdata):

        fig = go.Figure(data=[go.Candlestick(x=marketdata['Date'],
            open=marketdata['Open'],
            high=marketdata['High'],
            low=marketdata['Low'],
            close=marketdata['Close'],
            name=f"{self.market.primaryCurrency}/{self.market.secondaryCurrency}"
            )])
        fig.update_layout(
            title=f"{self.market.primaryCurrency}/{self.market.secondaryCurrency}",
            xaxis_title="Date",
            yaxis_title=f"Price ({self.market.secondaryCurrency})",
            font=dict(
                family="Courier New, monospace",
                size=12,
                color="black"
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    def save_to_csv(self,marketdata):

        csv = self.md().save_market_data_to_csv(marketdata,
         self.market)
        st.write(csv)

    def return_bots(self):
        botlist = self.md().c.customBotApi.get_all_custom_bots()
        n = [[f'{x.name}| ROI: {x.roi}'][0] for x in botlist.result] # creates list of names
        # r = [x.roi for x in botlist.result]
        b = [x for x in botlist.result] #creates list of objects
        dic = dict(zip(b, n)) #creates zipped obj/names list
        botobj = st.sidebar.selectbox('MH Bots: ',b,format_func=lambda x: dic[x]) # where b bot object returned from dic[x] name list
        st.write(botobj.name)
        self.bots = botobj
        st.write(self.bots.name)

    def return_configs(self):
        files = []
        for file in os.listdir('./'):
            # if file.endswith(".csv") or file.endswith('.json'):
            if file.endswith(".csv"):
                files.append(os.path.join('./', file))
        file = st.sidebar.selectbox('Select config file', files)
        self.configs = pd.read_csv(file)
        self.num_configs = int(st.sidebar.slider('Num configs to use',1,len(self.configs)))
        

    def bt(self):
            try:
                for b in self.bots:
                    if self.num_configs>len(self.configs.index):
                        self.num_configs == len(self.configs.index)
                    else:
                        pass
            except:
                    if self.num_configs>len(self.configs.index):
                        self.num_configs == len(self.configs.index)
                    else:
                        pass
            configs = self.configs.sort_values(by='roi', ascending=False)[0:self.num_configs]
            configs.drop_duplicates()
            configs.reset_index(inplace=True,drop=True)
            configs.roi = 0
           
            bt_results = self.iterate_csv()
            filename = str(self.bots.name.replace('/','_'))+str("_")+str(datetime.date.today().month)+str('-')+str(datetime.date.today().day)+str("_")+str(len(bt_results))+str('multi.csv')
            bt_results.sort_values(by='roi', ascending=False, inplace=True)
            bt_results.drop_duplicates()
            bt_results.reset_index(inplace=True,drop=True)
            bt_results.to_csv(filename)
            
            if self.num_configs:
                for c in range(self.num_configs):
                    new_bot = self.client.customBotApi.clone_custom_bot_simple(self.bots.accountId,self.bots.guid,self.bots.name).result
                    # print(new_bot)
                    new_bot2 = self.client.customBotApi.backtest_custom_bot(new_bot.guid, self.depth)
                    # st.write(new_bot2.errorCode)
                    
                    self.BotDB().setup_bot_from_csv(new_bot2.result,bt_results.iloc[c])
    def iterate_csv(self):
        best_roi = 0
        
        configs = self.configs
        configs_table = st.empty()
        configs.roi[0:-1] = 0
        bot = self.bots
        cols = ['interval', 'signalconsensus', 'fcc', 'resetmiddle',
             'allowmidsells', 'matype', 'rsil', 'rsib', 'rsis', 'bbl', 'devup',
             'devdn', 'macdfast', 'macdslow', 'macdsign', 'trades', 'roi']
        for c in configs.columns:
            if c not in cols:
                configs.drop(c,axis=1,inplace=True)
        markets = self.client.marketDataApi.get_price_markets(bot.priceMarket.priceSource).result
        for market in markets:
            if market.primaryCurrency == bot.priceMarket.primaryCurrency:
                if market.secondaryCurrency == bot.priceMarket.secondaryCurrency:
                    if bot.currentTradeAmount< market.minimumTradeAmount:
                        bot.currentTradeAmount = market.minimumTradeAmount
        
        for i in configs.index:
            try:
                print('Current Backtest ROI: ', bt.roi,'%','best ROI:', best_roi,'%')
                print('\nTop 5 configs so far:\n')
                print(configs.sort_values(by='roi', ascending=False)[0:5])
                
            except:
                pass            
            
            config = configs.iloc[i]
            s = self.BotDB().setup_bot_from_csv(bot, config)
            try:
                print(s.errorCode)
            except Exception as e:
                print(e)
            bt = self.client.customBotApi.backtest_custom_bot_on_market(
                bot.accountId,
                bot.guid,
                int(self.depth),
                bot.priceMarket.primaryCurrency,
                bot.priceMarket.secondaryCurrency,
                bot.priceMarket.contractName).result
            # try:
            #     print(bt.errorCode)
            # except Exception as e:
            #     print(e)
            if bt.roi > best_roi:
                best_roi = bt.roi
            configs['roi'][i] = bt.roi
            configs_table = st.write(bt.roi)
            
            
            return configs

def streamlist_mad_hatter_stuff(streamlit):
    st = streamlit
    st._max_width_()
    st.get_creds()
    
    # st.setup_candlesize()
    st.setup_bt()
    
    configs = st.return_configs()
    # st.write(configs[0:5])
    st.stop()
    st.button('Load Bots')
    if st.button:
        st.return_bots()
    
    bt = st.button('Backtest')
    if bt:
        st.bt()

def market_data_downloader(streamlit):
        streamlit._max_width_()
        streamlit.get_creds()
        streamlit.market_selector()
        # streamlit.setup_candlesize()
        streamlit.setup_bt()
        # data = streamlit.fetch_data()

        data = streamlit.get_data()

        streamlit.plot_market_data(data)

        streamlit.save_to_csv(data)
            
        
def main():
    s = StreamlitHaasTool()
    b = StreamlitBotTool()
    bot = b.get_data()

if __name__ == '__main__':

    streamlit = StreamlitHaasTool()
    # streamlist_mad_hatter_stuff(streamlit)
    market_data_downloader(streamlit)