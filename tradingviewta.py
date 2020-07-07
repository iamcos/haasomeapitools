from tradingview_ta import TA_Handler

xlmbtc = TA_Handler()
xlmbtc.pair = "xlmbtc"
xlmbtc.interval = "1m"
#xlmbtc.driver = "chrome"
#xlmbtc.headless = True

xlmbtc.start_driver()
analysis = xlmbtc.get_analysis()

print(analysis)
#Example output: ["Buy", 3, 10, 17]