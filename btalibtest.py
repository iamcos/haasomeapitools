from btalib import indicator, indicators
import btalib
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go

data = pd.read_csv(
    '/Users/cosmos/GitHub/haasomeapitools/market_data/BINANCE|ADA|BNB.csv', parse_dates=True)
data.fillna(0)
print(data)
sma = btalib.sma(data, period=4)
# # sma = btalib.sma(df, period=15)
# print(sma.params.period)
# print(sma.p.period)
# print(sma.params['period'])
# print(list(sma.params))
# print(dict(sma.params))

# stochastic = btalib.stochastic(data,period = 5)
# print(stochastic.df)
first_close_price = data.Close.iloc[0]
ema = btalib.ema(data,_seed =first_close_price)

bbands = btalib.bbands(data,_ma=btalib.wma)
print(bbands.df)
newcols = []

# data2 = pd.merge(data,bbands.df,how='right',on='index')
# print(bbands)
data2 = data.join(bbands.df,how='outer')
data2.rename(columns={'mid': f"{bbands.p.period} mid",
                      'top': f"{bbands.p.devs} top", 'bot': f"{bbands.p.devs} bot"}.)
print(data2)
