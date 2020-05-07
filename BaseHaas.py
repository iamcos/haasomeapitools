import configserver
from haasomeapi.HaasomeClient import HaasomeClient


class Haas():

	"""
	Haasonline trading software interaction class: get botlist, marketdata, create bots and configure their parameters, initiate backtests and so forth can be done through this class
	"""
	def __init__(self):
		self.c = self.client
	def client(self):
		ip, secret = configserver.validateserverdata()
		haasomeClient = HaasomeClient(ip, secret)
		return haasomeClient


class Bot(Haas):
	def __init__(self):
		Haas.__init__(self)
