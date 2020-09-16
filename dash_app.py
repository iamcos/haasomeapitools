import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
from BaseHaas import MarketData
from datetime import datetime as dt
from threading import Timer
from sqlalchemy import create_engine
from BaseHaas import MarketData
from botsellector import BotSellector
import btalib
import dash_bootstrap_components as dbc
from collections import deque
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
import jsonpickle
import json


import sqlite3 as sqllite

empty_market_data = MarketData().empty_market_data_df()

def return_bot_by_guid(guid):
	print('returning bot')
	tb = TradeBot()
	mh = MadHatterBot()
	bot = tb.return_bot(guid)
	print('Trade BOT')
	if isinstance(bot, dict):
		 bot = mh.return_bot(guid)
	return bot

def return_trades(guid):
	h = MadHatterBot()
	bot = return_bot_by_guid(guid)
	trades = h.trades_to_df(bot)
	return trades


def trade_bots_dropdown():
	h = BotSellector()
	bots = h.get_all_trade_bots()
	bots_dropdown = [
		{'label': str(x.name), 'value': str(x.guid)} for x in bots]
	return bots_dropdown


def custom_bots_dropdown():
	h = BotSellector()
	bots = h.get_all_custom_bots()
	bots_dropdown = [
		{'label': str(x.name), 'value': str(x.guid)} for x in bots]
	return bots_dropdown

def get_ticks( pricemarket,primarycoin,secondarycoin, interval):
    h = MarketData()

    df = h.get_ticks(pricemarket, primarycoin,
                     secondarycoin, interval, 'DEEPTICKS')

    return df


def get_market_data_and_save_to_db( market, primarycoin, secondarycoin, interval, depth):

        marketobj = h.return_priceMarket_object( market, primarycoin, secondarycoin)
        market_history = h.get_market_data(marketobj.priceSource, marketobj.primaryCurrency, marketobj.secondaryCurrency, interval, depth)
        db= sqllite.connect(":memory:")
        # db_name = 'market.db'
        db_name = ":memory:"
        engine = create_engine("sqlite:///%s" % db_name,
                            execution_options={"sqlite_raw_colnames": True})
        table_name = f'{EnumPriceSource(marketobj.priceSource).name},{marketobj.primaryCurrency},{marketobj.secondaryCurrency},{interval}'
        # market_history.to_csv(f'{table_name}.csv')
        if market_history not in db:

            market_history.to_sql(
                table_name, con=engine, if_exists='append')
        return market_history


def get_market_data_via_haas( pricesource,primarycoin,secondarycoin, interval,depth):
    h = MarketData()

    marketobj = h.return_priceMarket_object(pricesource, primarycoin, secondarycoin)
    print(marketobj.priceSource)
    market_data = h.get_market_data(marketobj, interval, depth)

    return market_data

import btalib
def get_indicators():
    indicators = btalib.indicator.get_ind_by_name()
    # indicatorss = [[i.alias[-1], i] for i in indicators]
    # help(indicators[0])
    indicators_dropdown = [{'label':str(key),'value': str(key)} for key,value in indicators.items()]
    return indicators_dropdown


def markets_dropdown():
    h = MarketData()
    markets = h.get_all_markets()
    markets_dropdown = [{'label': str(x), 'value': str(
        x)} for x in markets.pricesource.unique()]
    return markets_dropdown

def primarycoin_dropdown(pricesource):
    h = MarketData()
    df = h.get_all_markets()
    pairs = df[df["pricesource"] == pricesource]
    primary_coin_dropdown = [{'label': str(x), 'value': str(
        x)} for x in pairs.primarycurrency.unique()]

    return primary_coin_dropdown

def secondary_coin_dropdown(primarycoin, pricesource):
    h = MarketData()
    df = h.get_all_markets()
    pairs = df[df["pricesource"] == pricesource][df['primarycurrency'] == primarycoin]
    # print(pairs)
    secondary_coin_dropdown = [{'label': str(x), 'value': str(
        x)} for x in pairs.secondarycurrency.unique()]
    # print(secondary_coin_dropdown)
    return secondary_coin_dropdown

market_viz = html.Div(
    [
        html.Div(id='market-object', style={'display': 'none'}),
        dbc.Row(
            [
                dbc.Col(dcc.Dropdown(id='pricesource', options=[
                                     o for o in markets_dropdown()], value="BINANCE"), width=2),
                dbc.Col(dcc.Dropdown(id='primarycoin', value='ADA'),width =2),
                dbc.Col(dcc.Dropdown(id='secondarycoin', value='BTC'),width =2)
            ]
                ),
        dbc.Row([dbc.Col(html.Div(id='coin-name'), style={'display': 'none'}),
                 dbc.Col(html.Div(id='indicator-data'),
                         style={'display': 'none'}),
                 dbc.Col(html.Div(id='market-data-df'),
                         style={'display': 'none'}),

                 ]),
        dbc.Row(dbc.Col(dcc.Graph(id='market-data'))),
        dbc.Row(dbc.Col(dcc.Dropdown(id='indicators', options=get_indicators()))),
        dbc.Row(
            [
                dbc.Col(dcc.Dropdown(id='botlist'	, options=[
                            o for o in custom_bots_dropdown()]))
            ]
        )
    ]
)



def app():
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

    # app.layout = html.Div([
    #     html.Label('Dropdown'),
    #     dcc.Dropdown(id='pricesource', options=[
    #                  o for o in markets_dropdown()]),
    #     dcc.Dropdown(id='primarycoin'),
    #     dcc.Dropdown(id='secondarycoin'),
    #     dcc.Graph(id='market-data'),
    #     dcc.Dropdown(id='botlist'	, options=[
    #         o for o in custom_bots_dropdown()]),
    #     ])

    app.layout = market_viz

    # @app.callback(Output('market-data1', 'figure'),
    #           [Input('graph-update', 'n_intervals')])
    # def update_graph_scatter(interval, pricesource=pricesource, primarycoin=primarycoin, secondarycoin=secondarycoin, empty_market_data=empty_market_data):
    #     md = MarketData()

    #     marketobj = md.return_priceMarket_object(pricesource,primarycoin,secondarycoin)
    #     print(marketobj)
    #     market_data = MarketData().get_last_minute_ticker(marketobj)
    #     empty_market_data.join(market_data)
    #     return empty_market_data

    @app.callback(Output("market-object",'children'),
                 [Input('pricesource', 'value'),
                  Input('primarycoin', 'value'),
                  Input('secondarycoin', 'value')])
    def get_market_obj(pricesource, primarycoin, secondarycoin):
        md=MarketData()
        market_obj = md.return_priceMarket_object(pricesource, primarycoin, secondarycoin)
        frozen = jsonpickle.encode(market_obj)
        return frozen
    @app.callback(Output('coin-name','children'),[Input("market-object",'children')])
    def update_coin_name(marketobj):
        market = mo['displayName'].split(" ")
        print(market)
        coin1, coin2 = pair.split('/')
        return market, coin1, coin2

    @app.callback(Output('indicator-data', 'children'), [Input('indicators', 'value'), Input('coin-name', 'children')])
    def make_indicator_plot(indicator,coin):
        md = MarketData()
        market, coin1, coin2 = coin
        # market_obj = md.return_priceMarket_object()

        market_data = md.get_ticks(market, coin1, coin2, 1, 'LASTTICKS')

        # indicator = jsonpickle.decode(indicator)
        indic = btalib.indicator.get_ind_by_name()
        # print(indic.__dict__)
        # print(indic)
        itis = indic[indicator](market_data)
        for i in itis:
            print(i.__dict__)
        print(itis)

        # return indicator(market_data).df
        # print('IND', indicator.df)




    @app.callback(
        Output(component_id='primarycoin', component_property='options'),
        [Input(component_id='pricesource', component_property='value')]
    )
    def update_output_dropdown(input_value):
        pc = primarycoin_dropdown(input_value)
        return pc

    @app.callback(
        Output(component_id='secondarycoin', component_property='options'),
        [Input(component_id='primarycoin', component_property='value'),
         Input(component_id='pricesource', component_property='value'), ]
    )
    def update_output_dropdown2(primarycoin, pricesource):
        pc = secondary_coin_dropdown(primarycoin, pricesource)
        return pc

    @app.callback(Output(
        'market-data-df', 'children'),
        # [Input('pricesource', 'value'),
        # Input('primarycoin', 'value'),
        # Input('secondarycoin', 'value')])
        [Input('market-object', 'children')])

    def get_market_Data(frozen):
            market_object = jsonpickle.decode(frozen)

            market_data = MarketData().get_ticks(
                EnumPriceSource(market_object.priceSource).name, market_object.primaryCurrency, market_object.secondaryCurrency, 1, 'LASTTICKS')
            frozen = market_data.to_json()
            return frozen

    @app.callback(Output('market-data', 'figure'), [Input('market-data-df', 'children')])
    def plot(frozen):
        market_data =  pd.read_json(frozen)
        fig = go.Figure(
            # data=[go.Scatter(x=market_data.T, y=market_data.high)])
            data=[go.Candlestick(x=market_data.index, open=market_data.open, high=market_data.high, low=market_data.low, close=market_data.close)])
        # print(f" FIGURE DICTIONARY \n {fig.__dict__}")
        return fig

    return app

if __name__ == '__main__':
    app = app()
    app.run_server(debug=True)
