from BaseHaas import Haas, Bot
from functools import lru_cache
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from botsellector import BotSellector
from IndicatorsClass import IndicatorConfiguations as ic
from haasomeapi.enums.EnumIndicator import EnumIndicator
import pandas as pd
class TradeBot(Bot):

	def __init__(self):
		Bot.__init__(self)


	def get_indicators(self,bot):
		'''
		returns all tradebot indicators as a list
		'''

		idd = list([bot.indicators[x] for x in bot.indicators])
		return idd

	def select_indicator(self,indicators):

		for i, b in enumerate(indicators):
			print(i, indicators[i].indicatorTypeFullName)
		uip = input('Select indicator')

		indicator = indicators[int(uip)]
		print('select indicator', indicator)
		return indicator
	def setup_indicator(self,bot,indicator):
		setup = self.c.TradeBotApi.setup_indicator(bot.guid, indicator.guid,
                                       bot.priceMarket, bot.priceMarket.primaryCurrency, bot.priceMarket.secondaryCurrency, bot.priceMarket.contractName, indicator.timer, indicator.chartType, indicator.deviation)
		print(f'Indicator setup was a {setup.errorCode.value}, {setup.errorMessage.value}')
	def get_interfaces(self, bot, indicator):
		# print('indicator2', bot.indicators.__dict__)
		#returns select indicator interfaces
		# print(indicator.__dict__)
		interfaces = []
		for interface in bot.indicators[indicator.guid].indicatorInterface:
			interfaces.append({'title': interface.title, 'value': interface.value, 'options': interface.options, 'step': interface.step})

		return interfaces



	# def get_full_interfaces(self, bot, indicator):
	# 	interfaces ={}
	# 	for interface in bot.indicators[indicator.guid].indicatorInterface:
	# 		interfaces[EnumIndicator(bot.indicators[indicator.guid].indicatorType).name] = interface

	# 	print(interfaces)

	# 	return interfaces


	def dict_from_class(self,cls):

		 return dict(
                     (key, value)
                     for (key, value) in cls.__dict__.items()

                 )
	def get_full_interfaces(self, bot, indicator):
		interfaces = {}
		for interface in bot.indicators[indicator.guid].indicatorInterface:
			interfaces[EnumIndicator(
				bot.indicators[indicator.guid].indicatorType).name] = self.dict_from_class(interface)

		# print(interfaces)


		return interfaces
	def get_enums_for_indicators(self, bot):
		icc = ic()
		indicators_enums = {}
		for indicator in bot.indicators:
			indicator_enum = icc().get_indicator_enum_data(
				bot.indicators[indicator].indicatorInterface.indicatorType)
			indicators.append(indicator_enum)
		return indicators_enums


		return indicators
	def add_indicator(self, bot, indicator):
		failed = []
		try:
			add = self.c().tradeBotApi.add_indicator(bot.guid, indicator)
			if add.result:
				print('Indicator', EnumIndicator(indicator).name, ' added to ', bot.name)
			else:
				print('Adding indicator didn\'t work out')

		except:
			failed.append(indicator)
		return failed


	def edit_indicator(self, bot, indicator, field, value):
		print(indicator)
		indicator_config = self.c().tradeBotApi.edit_bot_indicator_settings(
			bot.guid, indicator.guid, field, value)
		# print('field',field,'value',value)
		# print(indicator_config.errorMessage, indicator_config.errorCode)
		# print('edit_indicators get indicator interface', indicator)
		interfaces = self.get_interfaces(bot, indicator)
		# for interface in interfaces:
		# 	print(interface)
		# print(indicator_config.result.__dict__)
		# print(indicator_config.result.name)
		# print(indicator_config.result.Indicators[indicator.guid])
		return indicator_config

	def remove_indicator(self, bot, indicator):
		failed = []
		try:
			add = self.c().tradeBotApi.remove_indicator(bot.guid, indicator.guid)
			if add.result:
				print('Indicator', EnumIndicator(indicator).value, ' removed from ', bot.name)
			else:
				print('Removing indicator didn\'t work out')

		except:
			failed.append(indicator)
		return failed

	def remove_indicators(self, bot, indicator_list):
		for x in indicator_list:
			self.remove_indicator(bot, x)


	def add_multiple_indicators(self, bot, indicators):
		for x in indicators:
			self.add_indicator(bot, x)

	def add_all_indicators(self,bot):
		indicators = [x for x in range(71)]
		self.add_multiple_indicators(bot,indicators)

	def remove_all_indicators(self,bot):
		indicators = t.get_indicators(bot)
		self.remove_indicators(bot, indicators)

	def select_bot_get_indicator(self,bot):
		indicators = self.get_indicators(bot)
		indicator = self.select_indicator(indicators)
		return indicator
