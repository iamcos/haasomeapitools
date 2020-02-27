import dash
import dash_core_components as dcc
import dash_html_components as html
# import botsellector
# import configserver
# import init
from botdatabase import BotDB
# from botinterface import BotInterface as BI
import plotly.graph_objs as go

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# bi = BI()

app = dash.Dash()
app.layout = html.Div([
    html.H1(children="yo")])


if __name__ == "__main__":
    app.run_server(debug=True)
