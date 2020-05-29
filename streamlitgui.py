import datetime
from math import pi
import streamlit as st
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
from MarketDataClass import MarketData as md
import dtale
import os
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models.widgets import Dropdown
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.plotting import figure, output_file, show

from bokeh.models import BooleanFilter, CDSView, Select, Range1d, HoverTool
from bokeh.palettes import Category20
from bokeh.models.formatters import NumeralTickFormatter
from botdb import BotDB
from bokeh.models import CustomJS, ColumnDataSource, HoverTool, NumeralTickFormatter
from haasomeapi.enums.EnumPriceSource import EnumPriceSource

from ratelimit import limits, sleep_and_retry
# data_load_state = st.text('Loading data...')



def market_selector():
    markets = md().get_all_markets()
    pricesource = st.sidebar.selectbox(
        'Select Exchange',
        (markets.pricesource.unique()), index=2)

    primarycurrency = st.sidebar.selectbox(
        'Primary coin', (md().primarycoin_dropdown(pricesource)))
    secondarycurrency = st.sidebar.selectbox('Secondary coin',(md().secondary_coin_dropdown(pricesource,primarycurrency)))

    market_object = md().return_priceMarket_object(pricesource,primarycurrency,secondarycurrency)
    st.title(
        f'Haasonline market data dashboard. {pricesource},{primarycurrency},{secondarycurrency}')
    # market_object.reset_index(inplace=True)
    return market_object



@st.cache
def get_data(marketobject, start, ticks):
    data = md().get_market_data(marketobject, 5, ticks)
    data['Open'] = data['open']
    data['Date'] = data['date']
    data['Close'] = data['close']
    data['High'] = data['high']
    data['Low'] = data['low']

    data.drop(['open', 'date', 'close', 'high', 'low'], axis=1, inplace=True)
    data.reset_index(inplace=True)
    return data

@st.cache
def get_data2(marketobject, start, ticks):
    data = md().get_market_data(marketobject, 5, ticks)

    data.reset_index(inplace=True)
    # data.set_index('Date')

    return data


# @st.cache
def cleanString(string):
    return string.translate({ord('$'): None})


def candlestick_plot(df, name):
    # Select the datetime format for the x axis depending on the timeframe
    xaxis_dt_format = '%d %b %Y'

    # if df['Date'][0].hour > 0:
    #     xaxis_dt_format = '%d %b %Y, %H:%M:%S'

    #more on https://docs.bokeh.org/en/latest/docs/reference/themes.html
    curdoc().theme = 'dark_minimal'
    fig = figure(sizing_mode='scale_both',
                 tools="xpan,xwheel_zoom,reset,save",
                 active_drag='xpan',
                 active_scroll='xwheel_zoom',
                 x_axis_type='linear',
                #  height = 500,
                # ,
                 #x_range=Range1d(df.index[0], df.index[-1]),
                 title=name
                 )

    fig.background_fill_color = 'black'
    fig.xgrid.grid_line_color = None
    fig.ygrid.grid_line_alpha = 0.5
    fig.xaxis.major_label_text_font_size = "16pt"
    fig.yaxis.major_label_text_font_size = "16pt"
    fig.title.text_font_size = "18pt"
    fig.yaxis[0].formatter = NumeralTickFormatter(format="$5.2f")
    inc = df.Close > df.Open
    dec = ~inc

    # Colour scheme for increasing and descending candles
    INCREASING_COLOR = '#009E73'
    DECREASING_COLOR = '#9E002A'

    width = 0.5
    inc_source = ColumnDataSource(data=dict(
        x1=df.index[inc],
        top1=df.Open[inc],
        bottom1=df.Close[inc],
        high1=df.High[inc],
        low1=df.Low[inc],
        Date1=df.Date[inc]
    ))

    dec_source = ColumnDataSource(data=dict(
        x2=df.index[dec],
        top2=df.Open[dec],
        bottom2=df.Close[dec],
        high2=df.High[dec],
        low2=df.Low[dec],
        Date2=df.Date[dec]
    ))
    # Plot candles
    # High and low
    fig.segment(x0='x1', y0='high1', x1='x1', y1='low1',
                source=inc_source, color=INCREASING_COLOR)
    fig.segment(x0='x2', y0='high2', x1='x2', y1='low2',
                source=dec_source, color=DECREASING_COLOR)

    # Open and close
    r1 = fig.vbar(x='x1', width=width, top='top1', bottom='bottom1', source=inc_source,
                    fill_color=INCREASING_COLOR, line_color=INCREASING_COLOR)
    r2 = fig.vbar(x='x2', width=width, top='top2', bottom='bottom2', source=dec_source,
                    fill_color=DECREASING_COLOR, line_color=DECREASING_COLOR)

    # Add on extra lines (e.g. moving averages) here
    # fig.line(df.index, <your data>)

    # Add on a vertical line to indicate a trading signal here
    #vlineIncreasing = Span(location=235, dimension='width',
    #              line_color="red", line_width=2)
    #vlineDecreasing = Span(location=150, dimension='width',
    #              line_color="green", line_width=2)
    #fig.renderers.extend([vlineIncreasing,vlineDecreasing])

    # Add date labels to x axis
    fig.xaxis.major_label_overrides = {
        i: date.strftime(xaxis_dt_format) for i, date in enumerate(pd.to_datetime(df["Date"]))
    }

    # Set up the hover tooltip to display some useful data
    fig.add_tools(HoverTool(
        renderers=[r1],
        tooltips=[
            ("Open", "$@top1"),
            ("High", "$@high1"),
            ("Low", "$@low1"),
            ("Close", "$@bottom1"),
            ("Date", "@Date1{" + xaxis_dt_format + "}"),
        ],
        formatters={
            'Date1': 'datetime',
        }))

    fig.add_tools(HoverTool(
        renderers=[r2],
        tooltips=[
            ("Open", "$@top2"),
            ("High", "$@high2"),
            ("Low", "$@low2"),
            ("Close", "$@bottom2"),
            ("Date", "@Date2{" + xaxis_dt_format + "}")
        ],
        formatters={
            'Date2': 'datetime'
        }))

    # JavaScript callback function to automatically zoom the Y axis to
    # view the data properly
    source = ColumnDataSource(
        {'Index': df.index, 'High': df.High, 'Low': df.Low})
    callback = CustomJS(args={'y_range': fig.y_range, 'source': source}, code='''
        clearTimeout(window._autoscale_timeout);
        var Index = source.data.Index,
            Low = source.data.Low,
            High = source.data.High,
            start = cb_obj.start,
            end = cb_obj.end,
            min = Infinity,
            max = -Infinity;
        for (var i=0; i < Index.length; ++i) {
            if (start <= Index[i] && Index[i] <= end) {
                max = Math.max(High[i], max);
                min = Math.min(Low[i], min);
            }
        }
        var pad = (max - min) * .05;
        window._autoscale_timeout = setTimeout(function() {
            y_range.start = min - pad;
            y_range.end = max + pad;
        });
    ''')

    # Finalise the figure
    # fig.width_policy = "auto"

    fig.x_range.js_on_change('start', callback)
    return fig


market = market_selector()

date = st.sidebar.date_input('Select starting bt date',
                     value=(datetime.date.today() - datetime.timedelta(days=1)))
time = st.sidebar.time_input('Select starting time')

dto = datetime.datetime.combine(date,time)
bd = BotDB()
depth = bd.calculate_ticks(dto)
# # st.write(market)
# market_data2 = get_data(market, 5, depth)
# # market_data2
marketdata = get_data2(market, 5, depth)

fig = candlestick_plot(
    marketdata, f"{EnumPriceSource(market.priceSource).name},{market.primaryCurrency}/{market.secondaryCurrency}")
st.bokeh_chart(fig, )
# st.bar_chart(marketdata)

# st.altair_chart(marketdata)

csv = md().save_market_data_to_csv(marketdata, market)
st.write(csv)
