def bruteforce_rsi_corridor(self, bot):
        rsi_l = int(bot.rsi['RsiLength'])
        applied = []
        bots = []
        print(rsi_l)
        d = [x for x in [rsi_l, rsi_l+1, rsi_l+2]]
        for x in d:
            print(x)
            botconfig = self.bot_config(bot)
            # print(botconfig)
            botconfig['rsil'] = x

            config, botobj = self.setup(bot, botconfig)
            applied.append(config)
        for x in range(rsi_l-3, bot.rsi['RsiLength'], -1):
            botconfig = self.bot_config(bot)
            botconfig['rsil'] = x

            config, botobj = self.setup(bot, botconfig)
            applied.append(config)