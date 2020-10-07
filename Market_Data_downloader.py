import datetime
from math import pi
import streamlit as st
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
from BaseHaas import MarketData as md
from BaseHaas import Haas, BotDB
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

from bokeh.models import CustomJS, ColumnDataSource, HoverTool, NumeralTickFormatter
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
from ratelimit import limits, sleep_and_retry
import configparser as cp
class Streamlit_interface:
    def __init__(self):
        self.md = md
 
        self.market = None
        self.depth = int(0)
        self.interval = int(0)

    def get_creds(self):
        adr = st.sidebar.text_input('Server ip: ')
        port = st.sidebar.text_input('Server port:')
        secret = st.sidebar.text_input('API key/secret: ')

        ip = str('http://'+adr+':'+port)
        client = HaasomeClient(ip, secret)
        self.client = client
        md = self.md.c = client
        


    def market_selector(self):
        markets = self.md.get_all_markets(self.md())
        pricesource = st.sidebar.selectbox(
            'Select Exchange',
            (markets.pricesource.unique()), index=2)

        primarycurrency = st.sidebar.selectbox(
            'Primary coin', (self.md.primarycoin_dropdown(self.md(),pricesource)))
        secondarycurrency = st.sidebar.selectbox(
            'Secondary coin', (self.md.secondary_coin_dropdown(self.md(),pricesource, primarycurrency)))
        market_object = self.md.return_priceMarket_object(self.md(),
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
            data = self.md.get_market_data(self.md(),self.market, self.interval, self.depth)
            return data
        
  

    def setup_bt(self):
        date = st.sidebar.date_input('Select starting bt date',
                                    value=(datetime.date.today() - datetime.timedelta(days=1)))
        time = st.sidebar.time_input('Select starting time')
        dto = datetime.datetime.combine(date, time)
        today = datetime.datetime.today()
        diff = today-dto
        interval = st.sidebar.selectbox(
            'Candle size', ([1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 45, 60, 90, 120]))
        depth = int(diff.total_seconds()/60
        /int(interval))
        print('date ', date, 'time ', time, 'diff ',
            diff, 'depth ', depth, 'interval', interval)
        self.depth = depth
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
        st.plotly_chart(fig,  use_container_width=False)

    def save_to_csv(self,marketdata):

        csv = self.md.save_market_data_to_csv(self.md(),marketdata,
         self.market)
        st.write(csv)

def main(streamlit):
        streamlit.get_creds()
        streamlit.market_selector()
        streamlit.setup_bt()
        # data = streamlit.fetch_data()
       
        data = streamlit.get_data()

        # streamlit.save_to_csv(data)
            
        
        streamlit.plot_market_data(data)
        
if __name__ == '__main__':
    s = Streamlit_interface()
    main(s)