import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
from MarketDataClass import MarketData
from datetime import datetime as dt
from threading import Timer
from sqlalchemy import create_engine
from MarketDataClass import MarketData
import btalib

import sqlite3 as sqllite

# def plot_market_data(self, pricemarket, primarycoin, secondarycoin,ticks):
#     # market_data = get_market_data_via_haas(
#     #     pricemarket, primarycoin, secondarycoin, ticks)
#     market_data = get_ticks(pricemarket, primarycoin,secondarycoin,interval)

#     fig = go.Figure(
#         data =[go.Scatter(x = market_data.D, y = market_data.H)])
#     return fig

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



def app():
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div([
        html.Label('Dropdown'),
        dcc.Dropdown(id='pricesource', options=[
                     o for o in markets_dropdown()]),
        dcc.Dropdown(id='primarycoin'),
        dcc.Dropdown(id='secondarycoin'),
        dcc.Graph(id = 'market-data')])

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
    @app.callback(dash.dependencies.Output(
            'market-data', 'figure'),
        [dash.dependencies.Input('pricesource', 'value'),
            dash.dependencies.Input('primarycoin', 'value'),
            dash.dependencies.Input('secondarycoin', 'value')])
            # dash.dependencies.Input('output-container-date-picker-range', 'children')])
    def plot_market_data( pricesource, primarycoin, secondarycoin):
        market_data = MarketData().get_ticks(
            pricesource, primarycoin, secondarycoin,1,'LASTTICKS')
        fig = go.Figure(
            # data=[go.Scatter(x=market_data.T, y=market_data.high)])
            data=[go.Candlestick(x=market_data.index, open=market_data.open, high=market_data.high, low=market_data.low, close=market_data.close)])
        return fig



    return app

if __name__ == '__main__':
    app = app()
    app.run_server(debug=True)
