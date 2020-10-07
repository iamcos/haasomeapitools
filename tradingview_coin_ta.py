from tradingview_ta import TA_Handler, Interval
symbol = 'BTCUSDT'

exchange = 'BINANCE'
pair = TA_Handler()
pair.set_symbol_as(symbol)
pair.set_exchange_as_crypto_or_stock(exchange)
pair.set_screener_as_crypto()
pair.set_interval_as(Interval.INTERVAL_1_DAY)
print(pair.get_analysis().summary)
# Example output: {"RECOMMENDATION": "BUY", "BUY": 8, "NEUTRAL": 6, "SELL": 3}
print(pair.get_analysis().oscillators)
print(pair.get_analysis().moving_averages)
print(pair.get_analysis().indicators)