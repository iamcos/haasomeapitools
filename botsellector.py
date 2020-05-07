from haasomeapi.enums.EnumFlashSpreadOptions import EnumFlashSpreadOptions
from haasomeapi.HaasomeClient import HaasomeClient
import configserver
import init
import re


class BotSellector:
	def __init__(self):
		self.c = self.client
	def client(self):
		ip, secret = configserver.validateserverdata()
		haasomeClient = HaasomeClient(ip, secret)
		return haasomeClient
	def return_bot(self, guid):
		bot = self.c.customBotApi.get_custom_bot(
			guid, EnumCustomBotType.MAD_HATTER_BOT)

		return bot.result
	def get_all_trade_bots(self):
		#Returns all Trade Bots as a list
		allbots = self.c().tradeBotApi.get_all_trade_bots().result
		return allbots

	def get_all_custom_bots(self):

		all_custom_bots = self.c().customBotApi.get_all_custom_bots().result
		return all_custom_bots


	def get_specific_bot(self,botlist):
		#Takes botlist and returns a single bot from it
		for i, x in enumerate(botlist):
			print(i, x.name, "ROI : ", x.roi, "with ", len(x.completedOrders), " trades")
		botnum = input(
			"Type bot number to use from the list above and hit return. \n Your answer: "
		)
		try:
			botnumobj = botlist[int(botnum)]
		except ValueError:
			botnum = input(
				"Wrong symbol. Can only use numbers. Type bot number indecated at the start of the string here: "
			)
		except IndexError:
			botnum = input(
				"Bot number is out of range. Type the number that is present on the list and hit enter: "
			)
		finally:
			botnumobj = botlist[int(botnum)]

		print("Bot ", botnumobj.name + " is selected!")
		return botnumobj

	def get_trade_bot(self):
		#Returns a specific trade bot from trade_bot list as in a single step
		all_trade_bots = self.get_all_trade_bots()
		bot = self.get_specific_bot(all_trade_bots)
		return bot
	def get_mad_hatter_bot(self):
		all_bots = self.get_all_custom_bots()
		all_mh_bots = [x for x in all_bots if x.botType == 15]
		bot = self.get_specific_bot(all_mh_bots)
		return bot

	def return_all_fcb_bots(haasomeClient):
		#Returns all Flash-Crash Bots as list.
		everybot = haasomeClient.customBotApi.get_all_custom_bots().result
		allbots = []
		for i, x in enumerate(everybot):
			if x.botType == 6:
				allbots.append(x)
		for i, x in enumerate(allbots):
			print(
				i,
				x.name,
				"ROI : ",
				x.roi,
				"with ",
				len(x.completedOrders),
				" trades and PriceSpreadType: ",
				x.priceSpreadType,
				EnumFlashSpreadOptions(x.priceSpreadType),
			)
		return allbots


	def getallmhbots(haasomeClient):
		#Older version of returning a asingle mad-hatter bot from botlist.
		everybot = haasomeClient.customBotApi.get_all_custom_bots().result
		allmhbots = []
		for i, x in enumerate(everybot):
			if x.botType == 15:
				allmhbots.append(x)
		for i, x in enumerate(allmhbots):
			print(i, x.name, "ROI : ", x.roi, "with ", len(x.completedOrders), " trades")
		botnum = input(
			"Type bot number to use from the list above and hit return. \n Your answer: "
		)
		try:
			botnumobj = allmhbots[int(botnum)]
		except ValueError:
			botnum = input(
				"Wrong symbol. Can only use numbers. Type bot number indecated at the start of the string here: "
			)
		except IndexError:
			botnum = input(
				"Bot number is out of range. Type the number that is present on the list and hit enter: "
			)
		finally:
			botnumobj = allmhbots[int(botnum)]
		print("Bot ", botnumobj.name + " is selected!")
		return botnumobj

	def gets_pecific_mh_bot_list(haasomeClient):
		#part of Brute Forcer script command. Will be removed in future releases.
		everybot = haasomeClient.customBotApi.get_all_custom_bots().result
		allmhbots = []
		for i, x in enumerate(everybot):
			if x.botType == 15:
				if x.name.startswith('Tune'):
					allmhbots.append(x)
		print('There are ', len(allmhbots), 'in qeue with each having top 3 best results recreated as bots.')
		return allmhbots

	def getallfcbots(haasomeClient):
		#older get Flash-Crash bot command version that returns flash crash bot bot object
		everybot = haasomeClient.customBotApi.get_all_custom_bots().result
		allbots = []
		for i, x in enumerate(everybot):
			if x.botType == 6:
				allbots.append(x)
		for i, x in enumerate(allbots):
			print(
				i,
				x.name,
				"ROI : ",
				x.roi,
				"with ",
				len(x.completedOrders),
				" trades and PriceSpreadType: ",
				x.priceSpreadType,
				EnumFlashSpreadOptions(x.priceSpreadType),
			)
		botnum = input(
			"Type bot number to use from the list above and hit return. \n Your answer: "
		)
		try:
			botnumobj = allbots[int(botnum)]
		except ValueError:
			botnum = input(
				"Wrong symbol. Can only use numbers. Type bot number indecated at the start of the string here: "
			)
		except IndexError:
			botnum = input(
				"Bot number is out of range. Type the number that is present on the list and hit enter: "
			)
		finally:
			botnumobj = allbots[int(botnum)]
		print("Bot ", botnumobj.name + " is selected!")
		return botnumobj


	def getalltradebots(haasomeClient):
		#older version of Get a Trade bot script version. REturns a single bot object.
		everybot = haasomeClient.tradeBotApi.get_all_trade_bots().result
		for i, x in enumerate(everybot):
			print(
				i,
				x.name,
				"with ROI : ",
				x.roi,
				"with ",
				len(x.completedOrders),
				" trades with indicators ",
				len(x.indicators),
			)
		botnum = input(
			"Type bot number to use from the list above and hit return. \n Your answer: "
		)
		try:
			botnumobj = everybot[int(botnum)]
		except ValueError:
			botnum = input(
				"Wrong symbol. Can only use numbers. Type bot number indecated at the start of the string here: "
			)
		except IndexError:
			botnum = input(
				"Bot number is out of range. Type the number that is present on the list and hit enter: "
			)
		finally:
			botnumobj = everybot[int(botnum)]
		print("Bot ", botnumobj.name + " is selected!")
		return botnumobj



	def getallbots(haasomeClient):
		#Returns every custom and trade bot as a list
		everybot = []
		custombots = haasomeClient.customBotApi.get_all_custom_bots().result
		for x in custombots:
			everybot.append(x)
		tradebots = haasomeClient.tradeBotApi.get_all_trade_bots().result
		for x in tradebots:
			everybot.append(x)
		if len(everybot) == 0:
			print("\nThere are no Custom Bots and No Tradebots.")
		else:
			for i, x in enumerate(everybot):
				print(i, x.name)
			botnum = input(
				"Type bot number to use from the list above and hit return. \n Your answer: "
			)
			try:
				botnumobj = everybot[int(botnum)]
			except ValueError:
				botnum = input(
					"Wrong symbol. Can only use numbers. Type bot number indecated at the start of the string here: "
				)
			except IndexError:
				botnum = input(
					"Bot number is out of range. Type the number that is present on the list and hit enter: "
				)
			finally:
				botnumobj = everybot[int(botnum)]
			print("Bot ", botnumobj.name + " is selected!")
			return botnumobj
