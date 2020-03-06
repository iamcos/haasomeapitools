from init import connect as haasomeClient
from botsellector import get_mh_bot




def set_mh_params(bot, haasomeClient, mode='r', indicator=None, param=None, value=None,):

    if mode == 'r':
        bBands = {'Length': bot.bBands["Length"], 'Devup': bot.bBands["Devup"], 'Devdn': bot.bBands["Devdn"], 'MaType': bot.bBands["MaType"], 'Deviation': bot.bBands["Deviation"], "allowMidSell": bot.bBands["allowMidSell"], 'RequireFcc': bot.bBands["RequireFcc"]}
        rsi = {'Length': bot.rsi['Length'], 'Sell': bot.rsi['RsiOversold'], 'Buy': bot.rsi['RsiOverbought']}
        macd = {'MacdFast': bot.macd['MacdFast'], 'MacdSlow': bot.macd['MacdSlow'], 'MacdSign': bot.macd['MacdSign']}
        return bBands, rsi, macd
    elif mode == 'w':
        # if indicator = 'bBands':
        #     if bot.bBands[str(param)] != value:
        #          do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
        #             bot.guid,
        #             EnumMadHatterIndicators.BBANDS,
        #             0, value)
        #             if do.errorCode != EnumErrorCode.SUCCESS:
        #                 # pass
        #                 print(do.errorCode, do.errorMessage, indicator
        pass

    mh_indicators_dict = {'bBands': {'Length': {'Read': bot.bBands["Length"], 'Set': haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                0, param)},
                'Devup': {'Read': bot.bBands["Devup"], 'Set': haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                bot.guid,
                EnumMadHatterIndicators.BBANDS,
                1, param)},
                'Devdn': {'Read': bot.bBands["Devdn"], 'Set': haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                        bot.guid,
                        EnumMadHatterIndicators.BBANDS,
                        2, param)},

                'MaType': {'Read': bot.bBands["MaType"], 'Set': haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                        bot.guid,
                        EnumMadHatterIndicators.BBANDS,
                        3, param)},

                'Deviation': {'Read': bot.bBands["Deviation"], 'Set': haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                        bot.guid,
                        EnumMadHatterIndicators.BBANDS,
                        4, param)},

                'AllowMidSell': {'Read': bot.bBands["AllowMidSell"], 'Set': haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                        bot.guid,
                        EnumMadHatterIndicators.BBANDS,
                        5, param)},
                'RequireFcc': {'Read': bot.bBands["RequireFcc"], 'Set': haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                        bot.guid,
                        EnumMadHatterIndicators.BBANDS,
                        6, param)}},
        'rsi': {'Length': {'Read': bot.rsi["Length"], 'Set': haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
         bot.guid,
         EnumMadHatterIndicators.RSI,
         0, param)}, 'Length': {'Read': bot.rsi["Length"], 'Set': haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
         bot.guid,
         EnumMadHatterIndicators.RSI,
             0, param), 'Buy': {'Read': bot.rsi['RsiOverbought'], 'Write': haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(bot.guid, EnumMadHatterIndicators.RSI, 1, param)}, 'Sell': {'Read': bot.rsi["RsiOversold"], 'Set': haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(bot.guid, EnumMadHatterIndicators.RSI, 1, param)},
        'macd': {'MacdFast': {'Read': bot.macd['MacdFast'], 'Set': haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(bot.guid, EnumMadHatterIndicators.MACD, 0, param)},
                             'MacdSlow': {'Read': bot.macd['MacdSlow'], 'Set': haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(bot.guid, EnumMadHatterIndicators.MACD, 1, param)},
                             'MacdSign': {'Read': bot.macd["MacdSign"], 'Set': haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(bot.guid, EnumMadHatterIndicators.MACD, 1, param)}}
         }}}
    return

bot  = get_mh_bot(haasomeClient())
set_mh_params(bot, haasomeClient)
