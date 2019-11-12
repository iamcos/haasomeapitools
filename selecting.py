from __future__ import print_function, unicode_literals
import regex
from decimal import Decimal
from haasomeapi.HaasomeClient import HaasomeClient
from pprint import pprint

# ffrom puinquirer import style_from_dict, Token, prompt
# ffrom puinquirer import Validator, ValidationError
import configserver
from haasomeapi.enums.EnumCustomBotType import EnumCustomBotType
from licensing.models import *
from licensing.methods import Key, Helpers
import tuner

import time
from haasomeapi.apis.AccountDataApi import AccountDataApi
from haasomeapi.apis.ApiBase import ApiBase
from haasomeapi.apis.MarketDataApi import MarketDataApi
from haasomeapi.dataobjects.accountdata.BaseOrder import BaseOrder
from haasomeapi.dataobjects.custombots.BaseCustomBot import BaseCustomBot
from haasomeapi.dataobjects.custombots.MadHatterBot import MadHatterBot
from haasomeapi.dataobjects.marketdata.Market import Market
from haasomeapi.dataobjects.util.HaasomeClientResponse import HaasomeClientResponse
from haasomeapi.enums.EnumCurrencyType import EnumCurrencyType
from haasomeapi.enums.EnumCustomBotType import EnumCustomBotType
from haasomeapi.enums.EnumErrorCode import EnumErrorCode
from haasomeapi.enums.EnumFundPosition import EnumFundPosition
from haasomeapi.enums.EnumMadHatterIndicators import EnumMadHatterIndicators
from haasomeapi.enums.EnumMadHatterSafeties import EnumMadHatterSafeties
from haasomeapi.enums.EnumOrderType import EnumOrderType
from haasomeapi.enums.EnumPriceSource import EnumPriceSource




def tunersi(therange):
    for x in range(therange):
        tuneRsiLength(therange)


import init
haasomeClient = init.connect()
import botsellector
import interval as iiv


def create_trial():
    trial_key = Key.create_trial_key(
        "WyI1NzkyIiwibDV5QVVDV2VmQ08zYmNmbE9GWHdyVFFNK2hzb0l6YldPOVhUY0hQVSJd",
        3941,
        Helpers.GetMachineCode(),
    )
    if trial_key[0] == None:
        print("An error occurred: {0}".format(trial_key[1]))

    pubKey = "<RSAKeyValue><Modulus>sGbvxwdlDbqFXOMlVUnAF5ew0t0WpPW7rFpI5jHQOFkht/326dvh7t74RYeMpjy357NljouhpTLA3a6idnn4j6c3jmPWBkjZndGsPL4Bqm+fwE48nKpGPjkj4q/yzT4tHXBTyvaBjA8bVoCTnu+LiC4XEaLZRThGzIn5KQXKCigg6tQRy0GXE13XYFVz/x1mjFbT9/7dS8p85n8BuwlY5JvuBIQkKhuCNFfrUxBWyu87CFnXWjIupCD2VO/GbxaCvzrRjLZjAngLCMtZbYBALksqGPgTUN7ZM24XbPWyLtKPaXF2i4XRR9u6eTj5BfnLbKAU5PIVfjIS+vNYYogteQ==</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>"

    res = Key.activate(
        token="WyI1NzkyIiwibDV5QVVDV2VmQ08zYmNmbE9GWHdyVFFNK2hzb0l6YldPOVhUY0hQVSJd",
        rsa_pub_key=pubKey,
        product_id=3941,
        key=trial_key[0],
    )
    # machine_code=Helpers.GetMachineCode())

    if res[0] == None:  # or not Helpers.IsOnRightMachine(res[0])
        print("An error occurred: {0}".format(res[1]))
    else:
        print("Success")

        license_key = res[0]
        print("Feature 1: " + str(license_key.f1))
        print("License expires: " + str(license_key.expires))
    return trial_key


def verifylicense(trial_key):
    RSAPubKey = "<RSAKeyValue><Modulus>nz/GmQrJsY53isJ23svQM9ewz2E/rZI+mdhWV+YxIDn7fljNN5MBw7UPGcAUARQkPfpUPpkGEKjmBHvQh5jk5yvcuzIVNNlfew3PkmbnkZbjREM6PzvZumC8QYK2p4zrdLFlt7SfLZWiRNVnT2dO4ssnsxmv//V8IKVwX8dkEg8mXmviAU/VTQC4o+MJG0Lqinu76X241pJDHiWRGIErpBgUw455hRByEpkQvjBdVclIPhyhn46Kf5ZUQ3CImjaKkTkUTDkmSW8ieYUa4A3xe4JFgCBgfMWaX5CU5X3tuGL05ZO4jDoda2jdtWdsemq/uQykh+dsfxBSYHtQPLHTHw==</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>"
    auth = "WyI1NzkyIiwibDV5QVVDV2VmQ08zYmNmbE9GWHdyVFFNK2hzb0l6YldPOVhUY0hQVSJd"

    result = Key.activate(
        token=auth,
        rsa_pub_key=RSAPubKey,
        product_id=3349,
        key="ICVLD-VVSZR-ZTICT-YKGXL",
    )
    # machine_code=Helpers.GetMachineCode())

    if result[0] == None:  # or not Helpers.IsOnRightMachine(res[0]):
        # an error occurred or the key is invalid or it cannot be activated
        # (eg. the limit of activated devices was achieved)
        print("The license does not work: {0}".format(result[1]))
    else:
        # everything went fine if we are here!
        print("The license is valid!")


def allmarketshistory():
    basebotconfig = haasomeClient.customBotApi.get_custom_bot(
        guid, EnumCustomBotType.MAD_HATTER_BOT
    ).result
    marketdata = []
    historyresult = " "
    results = []
    marketobject = haasomeClient.marketDataApi.get_price_markets(
        basebotconfig.priceMarket.priceSource
    )
    marketobjectr = marketobject.result
    for i, v in enumerate(marketobjectr):
        gethistory = haasomeClient.marketDataApi.get_history_from_market(
            v, basebotconfig.interval, btinterval
        )
        print(
            "History for ",
            v.primaryCurrency,
            v.secondaryCurrency,
            gethistory.EnumErrorCode,
        )
        print(gethistory.re)


def probeallmarkets():
    basebotconfig = haasomeClient.customBotApi.get_custom_bot(
        guid, EnumCustomBotType.MAD_HATTER_BOT
    ).result
    marketdata = []
    etalonroi = basebotconfig.roi * 0.8
    historyresult = None
    results = []
    marketobject = haasomeClient.marketDataApi.get_price_markets(
        basebotconfig.priceMarket.priceSource
    )
    marketobjectr = marketobject.result
    for i, v in enumerate(marketobjectr):
        settradeammount = v.minimumTradeAmount * 10
        configuremadhatter = haasomeClient.customBotApi.setup_mad_hatter_bot(
            basebotconfig.name,
            basebotconfig.guid,
            basebotconfig.accountId,
            basebotconfig.priceMarket.primaryCurrency,
            basebotconfig.priceMarket.secondaryCurrency,
            v.contractName,
            basebotconfig.leverage,
            basebotconfig.customTemplate,
            basebotconfig.coinPosition,
            v.tradeFee,
            basebotconfig.amountType,
            settradeammount * 10,
            basebotconfig.useTwoSignals,
            basebotconfig.disableAfterStopLoss,
            basebotconfig.interval,
            basebotconfig.includeIncompleteInterval,
            basebotconfig.mappedBuySignal,
            basebotconfig.mappedSellSignal,
        )
        # gethistory = haasomeClient.marketDataApi.get_history_from_market(v,basebotconfig.interval,btinterval)
        # historyresult = gethistory.errorCode
        bt = haasomeClient.customBotApi.backtest_custom_bot_on_market(
            basebotconfig.accountId,
            basebotconfig.guid,
            btinterval,
            v.primaryCurrency,
            v.secondaryCurrency,
            v.contractName,
        )
        btr = bt.result
        results.append(
            [btr.roi, v.primaryCurrency, v.secondaryCurrency, v.contractName]
        )
        print([v.primaryCurrency, v.secondaryCurrency, btr.roi])
    resultssorted = sorted(results, key=lambda x: x[0], reverse=True)
    for i, x in enumerate(resultssorted)[10]:
        if x[0] >= etalonroi:
            newbot = haasomeClient.customBotApi.clone_custom_bot(
                basebotconfig.accountId,
                basebotconfig.guid,
                EnumCustomBotType.MAD_HATTER_BOT,
                x[i][1] + x[i][2] + x[i][0],
                x[i][1],
                x[i][2],
                x[i][3],
            )
            print("bot for ", x[1], x[2], "created")


def tune_timeinterval():
    basebotconfig = haasomeClient.customBotApi.get_custom_bot(
        guid, EnumCustomBotType.MAD_HATTER_BOT
    ).result
    marketdata = []
    marketobject = haasomeClient.marketDataApi.get_price_markets(
        basebotconfig.priceMarket.priceSource
    )
    marketobjectr = marketobject.result
    for i, v in enumerate(marketobjectr):
        if (
            marketobjectr[i].primaryCurrency
            == basebotconfig.priceMarket.primaryCurrency
            and marketobjectr[i].secondaryCurrency
            == basebotconfig.priceMarket.secondaryCurrency
        ):
            marketdata = marketobjectr[i]
    intervals = {
        "0 minutes": 0,
        "1 minutes": 1,
        "2 minutes": 2,
        "3 minutes": 3,
        "4 minutes": 4,
        "5 minutes": 5,
        "6 minutes": 6,
        "10 minutes": 10,
        "12 minutes": 12,
        "15 minutes": 15,
        "20 minutes": 20,
        "30 minutes": 30,
        "45 minutes": 45,
        "1 hour": 60,
        "1.5 hours": 90,
        "2 hours": 120,
        "2.5 hours": 150,
        "3 hours": 180,
        "4 hours": 240,
        "6 hours": 360,
        "12 hours": 720,
        "1 day": 1440,
        "2 days": 2880,
    }
    intervalindex = []
    intervalkeys = list(intervals.keys())
    intervalvalues = list(intervals.values())
    for n, i in enumerate(intervalvalues):
        if i == basebotconfig.interval:
            intervalindex = n
            answers = {"selection": None}
            print("Current bot interval: ", intervalindex, " Minutes")
            while answers["selection"] != "back":
                action = [
                    {
                        "type": "list",
                        "name": "selection",
                        "message": "Chose your next move: ",
                        "choices": ["increse", "decrease", "back"],
                    }
                ]
                if answers["selection"] == "increse":
                    basebotconfig = haasomeClient.customBotApi.get_custom_bot(
                        guid, EnumCustomBotType.BASE_CUSTOM_BOT
                    ).result
                    configuremadhatter = haasomeClient.customBotApi.setup_mad_hatter_bot(
                        basebotconfig.name,
                        basebotconfig.guid,
                        basebotconfig.accountId,
                        basebotconfig.priceMarket.primaryCurrency,
                        basebotconfig.priceMarket.secondaryCurrency,
                        marketdata.contractName,
                        basebotconfig.leverage,
                        basebotconfig.customTemplate,
                        basebotconfig.coinPosition,
                        marketdata.tradeFee,
                        basebotconfig.amountType,
                        basebotconfig.currentTradeAmount,
                        basebotconfig.useTwoSignals,
                        basebotconfig.disableAfterStopLoss,
                        intervalvalues[intervalindex],
                        basebotconfig.includeIncompleteInterval,
                        basebotconfig.mappedBuySignal,
                        basebotconfig.mappedSellSignal,
                    )

                    bt = haasomeClient.customBotApi.backtest_custom_bot_on_market(
                        basebotconfig.accountId,
                        basebotconfig.guid,
                        btinterval,
                        basebotconfig.priceMarket.primaryCurrency,
                        basebotconfig.priceMarket.secondaryCurrency,
                        marketdata.contractName,
                    )
                    # # print('backrtested mad hatter',bt.errorCode, bt.errorMessage)
                    btr = bt.result
                    print(btr.roi, " at", configuremadhatter.result.interval, "minutes")
                    intervalindex += 1
                elif answers["selection"] == "decrease":
                    basebotconfig = haasomeClient.customBotApi.get_custom_bot(
                        guid, EnumCustomBotType.BASE_CUSTOM_BOT
                    ).result
                    configuremadhatter = haasomeClient.customBotApi.setup_mad_hatter_bot(
                        basebotconfig.name,
                        basebotconfig.guid,
                        basebotconfig.accountId,
                        basebotconfig.priceMarket.primaryCurrency,
                        basebotconfig.priceMarket.secondaryCurrency,
                        marketdata.contractName,
                        basebotconfig.leverage,
                        basebotconfig.customTemplate,
                        basebotconfig.coinPosition,
                        marketdata.tradeFee,
                        basebotconfig.amountType,
                        basebotconfig.currentTradeAmount,
                        basebotconfig.useTwoSignals,
                        basebotconfig.disableAfterStopLoss,
                        intervalvalues[intervalindex],
                        basebotconfig.includeIncompleteInterval,
                        basebotconfig.mappedBuySignal,
                        basebotconfig.mappedSellSignal,
                    )
                    intervalindex -= 1
                    bt = haasomeClient.customBotApi.backtest_custom_bot_on_market(
                        basebotconfig.accountId,
                        basebotconfig.guid,
                        btinterval,
                        basebotconfig.priceMarket.primaryCurrency,
                        basebotconfig.priceMarket.secondaryCurrency,
                        marketdata.contractName,
                    )
                    # # print('backrtested mad hatter',bt.errorCode, bt.errorMessage)
                    btr = bt.result
                    print(btr.roi, " at", configuremadhatter.result.interval, "minutes")
                elif answers["selection"] == "back":
                    break
                answers = prompt(action)


### Helper classes ###

### Bot Selector ###

import botsellector


### Backtesting interval being redefined ###


### Trying full auto algo ###


def tune_timeinterval2():
    basebotconfig = haasomeClient.customBotApi.get_custom_bot(
        guid, EnumCustomBotType.BASE_CUSTOM_BOT
    ).result
    marketdata = []
    marketobject = haasomeClient.marketDataApi.get_price_markets(
        basebotconfig.priceMarket.priceSource
    )
    marketobjectr = marketobject.result
    for i, v in enumerate(marketobjectr):
        if (
            marketobjectr[i].primaryCurrency
            == basebotconfig.priceMarket.primaryCurrency
            and marketobjectr[i].secondaryCurrency
            == basebotconfig.priceMarket.secondaryCurrency
        ):
            marketdata = marketobjectr[i]

    intervals = {
        "0 minutes": 0,
        "1 minutes": 1,
        "2 minutes": 2,
        "3 minutes": 3,
        "4 minutes": 4,
        "5 minutes": 5,
        "6 minutes": 6,
        "10 minutes": 10,
        "12 minutes": 12,
        "15 minutes": 15,
        "20 minutes": 20,
        "30 minutes": 30,
        "45 minutes": 45,
        "1 hour": 60,
        "1.5 hours": 90,
        "2 hours": 120,
        "2.5 hours": 150,
        "3 hours": 180,
        "4 hours": 240,
        "6 hours": 360,
        "12 hours": 720,
        "1 day": 1440,
        "2 days": 2880,
    }
    initialinterval = basebotconfig.interval
    intervalindex = " "
    intervalkeys = list(intervals.keys())
    intervalvalues = list(intervals.values())
    paramroi = []
    for n, i in enumerate(intervalvalues):
        if i == basebotconfig.interval:
            intervalindex = n
            print("Current bot interval: ", intervalindex, " Minutes")

    if int(intervalindex) >= 0 and int(intervalindex) <= 12:
        print(intervalindex)
        configuremadhatter = haasomeClient.customBotApi.setup_mad_hatter_bot(
            basebotconfig.name,
            basebotconfig.guid,
            basebotconfig.accountId,
            basebotconfig.priceMarket.primaryCurrency,
            basebotconfig.priceMarket.secondaryCurrency,
            marketdata.contractName,
            basebotconfig.leverage,
            basebotconfig.customTemplate,
            basebotconfig.coinPosition,
            marketdata.tradeFee,
            basebotconfig.amountType,
            basebotconfig.currentTradeAmount,
            basebotconfig.useTwoSignals,
            basebotconfig.disableAfterStopLoss,
            intervalvalues[intervalindex],
            basebotconfig.includeIncompleteInterval,
            basebotconfig.mappedBuySignal,
            basebotconfig.mappedSellSignal,
        )

        print(configuremadhatter.result.interval, "minutes")
        bt = haasomeClient.customBotApi.backtest_custom_bot_on_market(
            basebotconfig.accountId,
            basebotconfig.guid,
            btinterval,
            basebotconfig.priceMarket.primaryCurrency,
            basebotconfig.priceMarket.secondaryCurrency,
            marketdata.contractName,
        )
        # # print('backrtested mad hatter',bt.errorCode, bt.errorMessage)
        btr = bt.result
        paramroi.append([btr.roi, intervalvalues[intervalindex]])
        print(btr.roi)
        intervalindex += 1
    while initialinterval > 1 and initialinterval <= 10:
        configuremadhatter = haasomeClient.customBotApi.setup_mad_hatter_bot(
            basebotconfig.name,
            basebotconfig.guid,
            basebotconfig.accountId,
            basebotconfig.priceMarket.primaryCurrency,
            basebotconfig.priceMarket.secondaryCurrency,
            marketdata.contractName,
            basebotconfig.leverage,
            basebotconfig.customTemplate,
            basebotconfig.coinPosition,
            marketdata.tradeFee,
            basebotconfig.amountType,
            basebotconfig.currentTradeAmount,
            basebotconfig.useTwoSignals,
            basebotconfig.disableAfterStopLoss,
            intervalvalues[intervalindex],
            basebotconfig.includeIncompleteInterval,
            basebotconfig.mappedBuySignal,
            basebotconfig.mappedSellSignal,
        )
        print(configuremadhatter.errorCode, configuremadhatter.errorMessage)
        print(configuremadhatter.result.interval, "minutes")
        bt = haasomeClient.customBotApi.backtest_custom_bot_on_market(
            basebotconfig.accountId,
            basebotconfig.guid,
            btinterval,
            basebotconfig.priceMarket.primaryCurrency,
            basebotconfig.priceMarket.secondaryCurrency,
            marketdata.contractName,
        )
        # print('backrtested mad hatter',bt.errorCode, bt.errorMessage)
        btr = bt.result
        print(btr.roi)
        paramroi.append([btr.roi, intervalvalues[intervalindex]])
        initialinterval -= 1

        paramroisorted = sorted(paramroi, key=lambda x: x[0], reverse=True)
        print(paramroisorted)
        configuremadhatter = haasomeClient.customBotApi.setup_mad_hatter_bot(
            basebotconfig.name,
            basebotconfig.guid,
            basebotconfig.accountId,
            basebotconfig.priceMarket.primaryCurrency,
            basebotconfig.priceMarket.secondaryCurrency,
            marketdata.contractName,
            basebotconfig.leverage,
            basebotconfig.customTemplate,
            basebotconfig.coinPosition,
            marketdata.tradeFee,
            basebotconfig.amountType,
            basebotconfig.currentTradeAmount,
            basebotconfig.useTwoSignals,
            basebotconfig.disableAfterStopLoss,
            paramroisorted[0][1],
            basebotconfig.includeIncompleteInterval,
            basebotconfig.mappedBuySignal,
            basebotconfig.mappedSellSignal,
        )
        print("best time interval has been set")

    #### RSI tuning 3 params together ###

    if rsiconfig[0][0] == 0 or rsiconfig[0][0] == Decimal(0.0):
        l -= 1
        setl(l)
        s += 1
        sets(s)
        b -= 1
        setb(b)
        if rsiconfig[1][0] >= rsiconfig[2][0] and rsiconfig[0][0] >= rsiconfig[1][0]:
            for x in range(2):
                l += 1
                setl(l)
                for x in range(2):
                    s += 1
                    sets(s)
                    b -= 1
                    setb(b)
                l -= 1
                setl(l)
                for x in range(2):
                    s += 1
                    sets(s)
                    b -= 1
                    setb(b)


def setbasicbotparameters():
    basebotconfig = haasomeClient.customBotApi.get_custom_bot(
        bot.guid, EnumCustomBotType.BASE_CUSTOM_BOT
    ).result
    haasomeClient.customBotApi.set_mad_hatter_safety_parameter(
        basebotconfig.guid, EnumMadHatterSafeties.STOP_LOSS, 0
    )
    haasomeClient.customBotApi.set_mad_hatter_safety_parameter(
        basebotconfig.guid, EnumMadHatterSafeties.PRICE_CHANGE_TO_BUY, 0
    )
    haasomeClient.customBotApi.set_mad_hatter_safety_parameter(
        basebotconfig.guid, EnumMadHatterSafeties.PRICE_CHANGE_TO_SELL, 0
    )
    print(
        "for the purposes of backtesting, STOPLOSS, %change to buy and sell has been set to zero"
    )
    haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
        basebotconfig.guid, EnumMadHatterIndicators.BBANDS, 6, False
    )
    haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
        basebotconfig.guid, EnumMadHatterIndicators.BBANDS, 7, False
    )
    haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
        basebotconfig.guid, EnumMadHatterIndicators.BBANDS, 8, False
    )
    print("FCC, Midell, Reset middle have been disabled for the same purposes")


### Helper classes ###


def settherange():
    therange = int(
        input(
            "Write the N% of backtests to be done at each operation. The recomended values are 3, 6, 12, 20"
        )
    )
    return int(therange)


### required data for script to work ###


bot = botsellector.getallmhbots(haasomeClient)
guid = bot.guid
import settimeinterval

btinterval = settimeinterval.settimeinterval()
setbasicbotparameters()

# answers = prompt(selectparametertochange())
import setbtrange

therange = setbtrange.settherange()
import startconfiguring

while True:
    selection = startconfiguring.startconfiguring(therange, guid, btinterval)
