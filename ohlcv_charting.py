import os
import sys
from asciichartpy import plot
import pandas as pd

# -----------------------------------------------------------------------------

this_folder = os.path.dirname(os.path.abspath(__file__))
root_folder = os.path.dirname(os.path.dirname(this_folder))
sys.path.append(root_folder + '/python')
sys.path.append(this_folder)

# -----------------------------------------------------------------------------



market = 'BINANCE'

symbol = 'BTC/USD'

# each ohlcv candle is a list of [ timestamp, open, high, low, close, volume ]
index = 'Close'  # use close price from each ohlcv candle


def print_chart(exchange, symbol):

    print("\n" + exchange + ' ' + symbol + ' chart:')

    # get a list of ohlcv candles
    ohlcv = pd.read_csv('market_data/BINANCE_BTC_USDT_SMALL.csv')
    close = ohlcv.Close.iloc[:150].values
    # get the ohlCv (closing price, index == 4)
    # series = [x for x in close]

    # print the chart
    print("\n" + plot(close[-120:-1], {'height': 10}))  # print the chart
    try:

        last = ohlcv.Close.iloc[-1]  # last closing price
    except Exception as e:
        print(e)
    return last

last = print_chart(market, symbol)
print("\n" + market + " ₿ = $" + str(last) + "\n")  # print last closing price
