from BaseHaas import Haas, Bot
from TradeBotClass import TradeBot
from BackTestingClass import BackTesting
from botsellector import BotSellector
from haasomeapi.dataobjects.custombots.dataobjects.Indicator import Indicator
from IndicatorsClass import IndicatorConfiguations as ic
import pandas as pd


# pip install --upgrade --force-reinstall numpy==1.14.5
# pip install --upgrade --force-reinstall pandas==0.22.0


def tradebotmain():
	h = TradeBot()
	bot = BotSellector().get_trade_bot()
	indicators = h.get_indicators(bot)
	indicator = h.select_indicator(indicators)
	print('indicator',indicator.__dict__)
	interfaces = h.get_interfaces(bot, indicator)

	print(interfaces)
	ticks = 200
	bt = h.c().customBotApi.backtest_custom_bot_on_market(
            bot.accountId,
            bot.guid,
            int(ticks),
            bot.priceMarket.primaryCurrency,
            bot.priceMarket.secondaryCurrency,
            bot.priceMarket.contractName,
        )
	print(bt.errorCode, bt.errorMessage)
	print(bt.result)



def bt():
	t = TradeBot()
	bot = BotSellector().get_trade_bot()
	print('bot',bot)
	indicators = t.get_indicators(bot)
	# print(,indicators)
	indicator = t.select_indicator(indicators)
	# print('indicator.guid',indicator.guid)
	bt = BackTesting()
	bt_range = bt.autocreate_ranges2(bot, indicator)
	d = bt.iterate_indicator(bot, indicator, bt_range)
	print(d[0].roi, d[1].roi, d[2].roi)

def indicators_play():
	t = TradeBot()
	bot = BotSellector().get_trade_bot()
	btt = BackTesting()
	# indicator = t.select_bot_get_indicator(bot)
	dd = btt.get_enums_for_indicators(bot)
	ddd = {key: value.__dict__ for key, value in dd.items()}
	ddd_keys = list(ddd.keys())
	# print(ddd_keys)
	ddd_vals = list(ddd.values())
	interface_items ={}
	for i in ddd_vals[0]['indicatorInterface']:
		 interface_items[i.__dict__[[]]](i.__dict__)
	# print(interface_items)

	ddd[ddd_keys[0]]['indicatorInterface'] = interface_items
	print(ddd)

	# print(dddd)
if __name__ == '__main__':
	bt()
