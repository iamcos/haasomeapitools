# Python
import plotly.offline as py
from fbprophet.plot import plot_plotly
import pandas as pd
from fbprophet import Prophet
df = pd.read_csv(
    '/Users/cosmos/GitHub/haasomeapitools/u.csv', parse_dates = ['Date'])


df2 = df[['Date', 'Close']].copy()
df2.columns = ['ds', 'y']
df2.head()
print(df2)
m = Prophet()
m.fit(df2)

future = m.make_future_dataframe(periods=365)
future.tail()
print(future)

forecast = m.predict(future)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
print(forecast)

fig1 = m.plot(forecast)

py.init_notebook_mode()

fig = plot_plotly(m, forecast)  # This returns a plotly Figure
py.iplot(fig)
