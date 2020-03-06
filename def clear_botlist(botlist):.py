def clear_botlist(botlist):
    cleanlist = []

    df = pd.DataFrame(botlist)

    i = 0
    new_list = [e for e in botlist if bot.bBands['Length'] and if bot.bBands['Devup'] and if bot.bBands['Devdn'] and if bot.bBands['MaType'] and if ]
    for len(botlist):
        for key, value in list(bot.bBands.keys()):

            if bot.bBands["Length"] != config_bot.bBands["Length"] and :
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.BBANDS,
                    0,
                    config_bot.bBands["Length"],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.erro/rCode, do.errorMessage, 'Length')
                except:
                    pass
            if bot.bBands["Devup"] != config_bot.bBands["Devup"]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.BBANDS,
                    1,
                    config_bot.bBands["Devup"],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'Devup')
                except:
                    pass
            if bot.bBands["Devdn"] != config_bot.bBands["Devdn"]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.BBANDS,
                    2,
                    config_bot.bBands["Devdn"],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                            pass
                            print(do.errorCode, do.errorMessage, 'Devdn')
                except:
                    pass
            if bot.bBands["MaType"] != config_bot.bBands["MaType"]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.BBANDS,
                    3,
                    config_bot.bBands["MaType"],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'MaType')
                except:
                    pass
            if bot.bBands["AllowMidSell"] != config_bot.bBands["AllowMidSell"]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.BBANDS,
                    5,
                    config_bot.bBands["AllowMidSell"],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'AllowMidSell')
                except:
                    pass
            if bot.bBands["RequireFcc"] != config_bot.bBands["RequireFcc"]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.BBANDS,
                    6,
                    config_bot.bBands["RequireFcc"],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'RequireFcc')
                except:
                    pass
            if bot.rsi["RsiLength"] != config_bot.rsi["RsiLength"]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.RSI,
                    0,
                    config_bot.rsi["RsiLength"],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'RsiLength')
                except:
                    pass
            if bot.rsi["RsiOverbought"] != config_bot.rsi["RsiOverbought"]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.RSI,
                    1,
                    config_bot.rsi["RsiOverbought"],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'RsiOverbought')
                except:
                    pass
            if bot.rsi["RsiOversold"] != config_bot.rsi["RsiOversold"]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.RSI,
                    2,
                    config_bot.rsi["RsiOversold"],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'RsiOversold')
                except:
                    pass
            if bot.macd["MacdFast"] != config_bot.macd["MacdFast"]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.MACD,
                    0,
                    config_bot.macd["MacdFast"],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                    print(do.errorCode, do.errorMessage, 'MacdFast')
                except:
                    pass
            if bot.macd["MacdSlow"] != config_bot.macd["MacdSlow"]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.MACD,
                    1,
                    config_bot.macd["MacdSlow"],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'MacdSlow')
                except:
                    pass

            if bot.macd["MacdSign"] != config_bot.macd["MacdSign"]:
                do = haasomeClient.customBotApi.set_mad_hatter_indicator_parameter(
                    bot.guid,
                    EnumMadHatterIndicators.MACD,
                    2,
                    config_bot.macd["MacdSign"],
                )
                try:
                    if do.errorCode != EnumErrorCode.SUCCESS:
                        # pass
                        print(do.errorCode, do.errorMessage, 'MacdSign')
                except:
                    pass

            else:

                print(bot.name, "indicators have been configured")
                return bot
            return do.result
        else:
                return bot
