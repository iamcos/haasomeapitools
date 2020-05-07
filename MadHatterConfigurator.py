from MadHatterBotClass import MadHatterBot
	class MadHatterConfigurator(MadHatterBot):

        def __init__(self):
            MadHatterBot.__init__

    def apply_config_to_madhatter_bot(self, bot, configs, ind):
            configs = configs.iloc[int]

			if bot.bBands["Length"] != configs['bbl']:
				do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
				bot.guid,
				EnumMadHatterIndicators.BBANDS,
				0,
					configs['bbl']
			)
			try:
				if do.errorCode != EnumErrorCode.SUCCESS:
					# pass
					print(do.erro/rCode, do.errorMessage, 'Length')
			except:
				pass
			if bot.bBands["Devup"] != configs['devup']:
				do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
					bot.guid,
					EnumMadHatterIndicators.BBANDS,
					1,
					configs['devup'],
				)
				try:
					if do.errorCode != EnumErrorCode.SUCCESS:
						# pass
						print(do.errorCode, do.errorMessage, 'Devup')
				except:
					pass
			if bot.bBands["Devdn"] != configs['devdn']:
				do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
					bot.guid,
					EnumMadHatterIndicators.BBANDS,
					2,
					configs['devdn'],
				)
				try:
					if do.errorCode != EnumErrorCode.SUCCESS:
							pass
							print(do.errorCode, do.errorMessage, 'Devdn')
				except:
					pass
			if bot.bBands["MaType"] != configs['matype']:
				do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
					bot.guid,
					EnumMadHatterIndicators.BBANDS,
					3,
					configs['matype'],
				)
				try:
					if do.errorCode != EnumErrorCode.SUCCESS:
						# pass
						print(do.errorCode, do.errorMessage, 'MaType')
				except:
					pass
			if bot.bBands["AllowMidSell"] != configs['allowmidsells']:
				do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
					bot.guid,
					EnumMadHatterIndicators.BBANDS,
					5,
					configs['allowmidsells'],
				)
				try:
					if do.errorCode != EnumErrorCode.SUCCESS:
						# pass
						print(do.errorCode, do.errorMessage, 'AllowMidSell')
				except:
					pass
			if bot.bBands["RequireFcc"] != configs['fcc']:
				do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
					bot.guid,
					EnumMadHatterIndicators.BBANDS,
					6,
					configs['fcc'],
				)
				try:
					if do.errorCode != EnumErrorCode.SUCCESS:
						# pass
						print(do.errorCode, do.errorMessage, 'RequireFcc')
				except:
					pass
			if bot.rsi["RsiLength"] != configs['rsil']:
				do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
					bot.guid,
					EnumMadHatterIndicators.RSI,
					0,
					configs['rsil'],
				)
				try:
					if do.errorCode != EnumErrorCode.SUCCESS:
						# pass
						print(do.errorCode, do.errorMessage, 'RsiLength')
				except:
					pass
			if bot.rsi["RsiOverbought"] != configs['rsib']:
				do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
					bot.guid,
					EnumMadHatterIndicators.RSI,
					1,
					configs['rsib'],
				)
				try:
					if do.errorCode != EnumErrorCode.SUCCESS:
						# pass
						print(do.errorCode, do.errorMessage, 'RsiOverbought')
				except:
					pass
			if bot.rsi["RsiOversold"] != configs['rsis']:
				do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
					bot.guid,
					EnumMadHatterIndicators.RSI,
					2,
					configs['rsis'],
				)
				try:
					if do.errorCode != EnumErrorCode.SUCCESS:
						# pass
						print(do.errorCode, do.errorMessage, 'RsiOversold')
				except:
					pass
			if bot.macd["MacdFast"] != configs['macdfast']:
				do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
					bot.guid,
					EnumMadHatterIndicators.MACD,
					0,
					configs['macdfast'],
				)
				try:
					if do.errorCode != EnumErrorCode.SUCCESS:
						# pass
						print(do.errorCode, do.errorMessage, 'MacdFast')
				except:
					pass
			if bot.macd["MacdSlow"] != configs['macdslow']:
				do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
					bot.guid,
					EnumMadHatterIndicators.MACD,
					1,
					configs['macdslow'],
				)
				try:
					if do.errorCode != EnumErrorCode.SUCCESS:
						# pass
						print(do.errorCode, do.errorMessage, 'MacdSlow')
				except:
					pass

			if bot.macd["MacdSign"] != configs['macdsign']:
				do = self.c().customBotApi.set_mad_hatter_indicator_parameter(
					bot.guid,
					EnumMadHatterIndicators.MACD,
					2,
					configs['macdsign'],
				)
				try:
					if do.errorCode != EnumErrorCode.SUCCESS:
						# pass
						print(do.errorCode, do.errorMessage, 'MacdSign')
				except:
					pass
			if bot.interval != configs['interval']:
				botname = str(bot.priceMarket.primaryCurrency) + str(' / ') + \
					str(bot.priceMarket.secondaryCurrency) + str(' Roi ') + str(bot.roi)
				setup_bot = self.c().customBotApi.setup_mad_hatter_bot(
				botName = bot.name,
				botGuid=bot.guid,
				accountGuid=bot.accountId,
				primaryCoin=bot.priceMarket.primaryCurrency,
				secondaryCoin=bot.priceMarket.secondaryCurrency,
				contractName=bot.priceMarket.contractName,
				leverage=bot.leverage,
				templateGuid=bot.customTemplate,
				position=bot.coinPosition,
				fee=bot.currentFeePercentage,
				tradeAmountType=bot.amountType,
				tradeAmount=bot.currentTradeAmount,
				useconsensus=bot.useTwoSignals,
				disableAfterStopLoss=bot.disableAfterStopLoss,
				interval=configs['interval'],
				includeIncompleteInterval=bot.includeIncompleteInterval,
				mappedBuySignal=bot.mappedBuySignal,
				mappedSellSignal=bot.mappedSellSignal,).result
				# print(bot.name,' Has been configured')

			else:
				print(bot.name,' Has been configured')
			bt = self.bt_mh(bot)
			botconfig = self.bot_config(bot)
			# configs['roi'] = bt.roi
			# configs['trades'] = len(bt.completedOrders)
			configs.sort_values(by='roi', ascending=False, inplace=True)
			print(configs)
			return configs
