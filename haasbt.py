
from haasomeapi.HaasomeClient import HaasomeClient
from haasomeapi.apis.MarketDataApi import MarketDataApi
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from haasomeapi.enums.EnumCustomBotType import EnumCustomBotType
from haasomeapi.dataobjects.custombots.BaseCustomBot import BaseCustomBot
from botdatabase import BotDB
import configserver
from backtesting import Backtest ,Strategy
from MarketDataClass import MarketData as md
from backtesting.lib import SignalStrategy, TrailingStrategy
# from MadHatterBotClass import MadHatterBot as mh
# from botdb import BotDB as bdb
md = md()
md = md.read_csv(
    '/Users/cosmos/GitHub/Haasomeapitools/haasomeapitools/market_data/BITFINEX|ABS|USD.csv')

print(md)
bt = Backtest(data=md, strategy=SignalStrategy()).run()
