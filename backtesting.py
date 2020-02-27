
from haasomeapi.HaasomeClient import HaasomeClient
from haasomeapi.apis.MarketDataApi import MarketDataApi
from haasomeapi.enums.EnumPriceSource import EnumPriceSource
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from haasomeapi.enums.EnumCustomBotType import EnumCustomBotType
from haasomeapi.dataobjects.custombots.BaseCustomBot import BaseCustomBot
from botdatabase import BotDB
import configserver


class ConfigFinder:
    def __init__(self):
        self.selected_bot = None
        self.rois = None
        self.completed_configs = None
        self.connect = HaasomeClient(
            self.connection_string[0], self.connection_string[1]
        )


    def set_mh_indicators(self,current_bot, config_bot, haasomeClient):

        if current_bot.bBands["Length"] != config_bot.bBands["Length"]:
            do = self.connect.customBotApi.set_mad_hatter_indicator_parameter(
                current_bot.guid,
                EnumMadHatterIndicators.BBANDS,
                0,
                config_bot.bBands["Length"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    pass
                # print(do.errorCode, do.errorMessage, 'Length')
            except:
                pass
        if current_bot.bBands["Devup"] != config_bot.bBands["Devup"]:
            do = self.connect.customBotApi.set_mad_hatter_indicator_parameter(
                current_bot.guid,
                EnumMadHatterIndicators.BBANDS,
                1,
                config_bot.bBands["Devup"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    pass
                # print(do.errorCode, do.errorMessage, 'Devup')
            except:
                pass
        if current_bot.bBands["Devdn"] != config_bot.bBands["Devdn"]:
            do = self.connect.customBotApi.set_mad_hatter_indicator_parameter(
                current_bot.guid,
                EnumMadHatterIndicators.BBANDS,
                2,
                config_bot.bBands["Devdn"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    pass
                # print(do.errorCode, do.errorMessage, 'Devdn')
            except:
                pass
        if current_bot.bBands["MaType"] != config_bot.bBands["MaType"]:
            do = self.connect.customBotApi.set_mad_hatter_indicator_parameter(
                current_bot.guid,
                EnumMadHatterIndicators.BBANDS,
                3,
                config_bot.bBands["MaType"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    pass
                # print(do.errorCode, do.errorMessage, 'MaType')
            except:
                pass
        if current_bot.bBands["AllowMidSell"] != config_bot.bBands["AllowMidSell"]:
            do = self.connect.customBotApi.set_mad_hatter_indicator_parameter(
                current_bot.guid,
                EnumMadHatterIndicators.BBANDS,
                5,
                config_bot.bBands["AllowMidSell"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    pass
                # print(do.errorCode, do.errorMessage, 'AllowMidSell')
            except:
                pass
        if current_bot.bBands["RequireFcc"] != config_bot.bBands["RequireFcc"]:
            do = self.connect.customBotApi.set_mad_hatter_indicator_parameter(
                current_bot.guid,
                EnumMadHatterIndicators.BBANDS,
                6,
                config_bot.bBands["RequireFcc"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    pass
                # print(do.errorCode, do.errorMessage, 'RequireFcc')
            except:
                pass
        if current_bot.rsi["RsiLength"] != config_bot.rsi["RsiLength"]:
            do = self.connect.customBotApi.set_mad_hatter_indicator_parameter(
                current_bot.guid,
                EnumMadHatterIndicators.RSI,
                0,
                config_bot.rsi["RsiLength"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    pass
                # print(do.errorCode, do.errorMessage, 'RsiLength')
            except:
                pass
        if current_bot.rsi["RsiOverbought"] != config_bot.rsi["RsiOverbought"]:
            do = self.connect.customBotApi.set_mad_hatter_indicator_parameter(
                current_bot.guid,
                EnumMadHatterIndicators.RSI,
                1,
                config_bot.rsi["RsiOverbought"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    pass
                # print(do.errorCode, do.errorMessage, 'RsiOverbought')
            except:
                pass
        if current_bot.rsi["RsiOversold"] != config_bot.rsi["RsiOversold"]:
            do = self.connect.customBotApi.set_mad_hatter_indicator_parameter(
                current_bot.guid,
                EnumMadHatterIndicators.RSI,
                2,
                config_bot.rsi["RsiOversold"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    pass
                # print(do.errorCode, do.errorMessage, 'RsiOversold')
            except:
                pass
        if current_bot.macd["MacdFast"] != config_bot.macd["MacdFast"]:
            do = self.connect.customBotApi.set_mad_hatter_indicator_parameter(
                current_bot.guid,
                EnumMadHatterIndicators.MACD,
                0,
                config_bot.macd["MacdFast"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    pass
                # print(do.errorCode, do.errorMessage, 'MacdFast')
            except:
                pass
        if current_bot.macd["MacdSlow"] != config_bot.macd["MacdSlow"]:
            do = self.connect.customBotApi.set_mad_hatter_indicator_parameter(
                current_bot.guid,
                EnumMadHatterIndicators.MACD,
                1,
                config_bot.macd["MacdSlow"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    pass
                # print(do.errorCode, do.errorMessage, 'MacdSlow')
            except:
                pass

        if current_bot.macd["MacdSign"] != config_bot.macd["MacdSign"]:
            do = self.connect.customBotApi.set_mad_hatter_indicator_parameter(
                current_bot.guid,
                EnumMadHatterIndicators.MACD,
                2,
                config_bot.macd["MacdSign"],
            )
            try:
                if do.errorCode != EnumErrorCode.SUCCESS:
                    pass
                # print(do.errorCode, do.errorMessage, 'MacdSign')
            except:
                pass

        else:
            return current_bot
            print(f'{current_bot.name} config has not been altered')
        print(current_bot.name, "indicators have been configured")
        return do.result


    def setup_mad_hatter_bot(bot, current_bot, haasomeClient):
        botname = (
            str(bot.priceMarket.primaryCurrency)
            + str(" / ")
            + str(bot.priceMarket.secondaryCurrency)
            + str(" Roi ")
            + str(current_bot.roi)
        )
        setup_bot = self.connect.customBotApi.setup_mad_hatter_bot(
            botName=botname,
            botGuid=current_bot.guid,
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
            interval=bot.interval,
            includeIncompleteInterval=bot.includeIncompleteInterval,
            mappedBuySignal=bot.mappedBuySignal,
            mappedSellSignal=bot.mappedSellSignal,
        )
        err(setup_bot)
        print(bot.name, " Has been configured")
        return setup_bot.result
