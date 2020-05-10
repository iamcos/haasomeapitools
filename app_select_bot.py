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
from botsellector import BotSellector
import sqlite3 as sqllite
from TradeBotClass import TradeBot
from MadHatterBotClass import MadHatterBot
import pandas as pd
from functools import lru_cache
import btalib
# def plot_market_data(self, pricemarket, primarycoin, secondarycoin,ticks):
#     # market_data = get_market_data_via_haas(
#     #     pricemarket, primarycoin, secondarycoin, ticks)
#     market_data = get_ticks(pricemarket, primarycoin,secondarycoin,interval)

#     fig = go.Figure(
#         data =[go.Scatter(x = market_data.D, y = market_data.H)])
#     return fig


def get_ticks(pricemarket, primarycoin, secondarycoin, interval):
	h = MarketData()

	df = h.get_ticks(pricemarket, primarycoin,
					 secondarycoin, interval, 'DEEPTICKS')

	return df


def return_bot_by_guid(guid):
	print('returning bot')
	tb = TradeBot()
	mh = MadHatterBot()
	bot = tb.return_bot(guid)
	print('Trade BOT')
	if isinstance(bot, dict):
		 bot = mh.return_bot(guid)
	return bot


def get_market_data_and_save_to_db(market, primarycoin, secondarycoin, interval, depth):

		marketobj = h.return_priceMarket_object(
			market, primarycoin, secondarycoin)
		market_history = h.get_market_data(
			marketobj.priceSource, marketobj.primaryCurrency, marketobj.secondaryCurrency, interval, depth)
		db = sqllite.connect(":memory:")
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


@lru_cache(maxsize=None)
def get_market_data_via_haas(guid):
	# print(bot)
	h = MarketData()
	bot = return_bot_by_guid(guid)
	# print(bot)
	# marketobj = h.return_priceMarket_object(pricesource, primarycoin, secondarycoin)
	# print(marketobj.priceSource)
	endUnix = pd.to_datetime(dt.utcnow())
	# print(endUnix)
	first_order_dt = pd.to_datetime(
		bot.completedOrders[0].unixAddedTime, unit='s')
	startUnix = endUnix - first_order_dt
	# print(startUnix.total_seconds()/60)
	depth = startUnix.total_seconds() / 60
	inter = 5
	market_data = h.get_market_data(bot.priceMarket, inter, int(depth)/inter)
	return market_data


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


def app():
	external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

	app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

	app.layout = html.Div([
		html.Label('Dropdown'),
		dcc.Dropdown(id='botlist'	, options=[
					 o for o in custom_bots_dropdown()]),
		dcc.Graph(id='market-data')])

	@app.callback(
		Output('market-data', 'figure'),
		[Input('botlist', 'value')]
	)
	def uppdate_market_data(bot):
		market_data = get_market_data_via_haas(bot)
		fig = go.Figure(
		   # data=[go.Scatter(x=market_data.T, y=market_data.high)])
		   data=[go.Candlestick(x=market_data.date, open=market_data.open, high=market_data.high, low=market_data.low, close=market_data.close)])
		trades = return_trades(bot)
		buy = trades[trades['orderType'] == 0]
		sell = trades[trades['orderType'] == 1]
		fig.add_trace(go.Scatter(
	       x=buy.date, y=buy.price, mode='markers+text',text=buy.price,textposition='bottom center'))
		fig.add_trace(go.Scatter(
	       x=sell.date, y=sell.price, mode='markers'))

		config = dict({'scrollZoom': True})
		fig.update_layout(
			autosize=True,
			height=1200,
			margin=dict(
                            l=50,
                            r=50,
                            b=100,
                            t=100,
                            pad=4
                        ),
		)

		# sma = btalib.sma(market_data.high)
		# fig.add_trace(go.Scatter(x=market_data.data,y=sma))
		return fig

	return app



if __name__ == '__main__':
	app = app()
	app.run_server(debug=True)
