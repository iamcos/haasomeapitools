# haasomeapitools


botdatabase file execution runs iteration algorithm over around 700 mad-hatter configs that are stored in csv files alongside.
  with botdatabase is possible to load and save bots to files in json and csv or into a database.
  
botinterface contains a class that can be imported to any pythong script and enable basic HaasAPI integration.

Scripts to interact with Haasomeapi via the python wrapper

Based on haasomeapi, are scripts that accomplish various tasks with Haas:



botsellector.py is about selecting bots of every supported type as single botobject or as a list for further manipulations.
configserver.py is responsible for writing a config file to connect to haasonline via localapi

history.py allows for market data manipulation: save  it, turn it into a dataframe.

init.py is basic initialisation algorithm.
interval.py reads and writes backtesting interval and passes the number of ticks to evert backtested bot.

bots.haasbots contains a set of 900 mad hatter bot configurations for you to explore.

bt.ini should be put into user folder on your machine for it to initialize and launch atm.

tradeBot.py contains the basic tradeBot interaction scripts.
