
# Haasomeapi Tools

## Installation

1. Copy config.ini.example to config.ini
2. Update the server_address and secret with your Haas Trade Server Local API
3. Install Python

These scripts build upon haasomeapi Haas api pythong wrapper written by tallented R4stl1n for Haas.
## UPDATE
### Haasomeapi_example.ipynb
Interactive example-tutorial jupyter notebook with interactive code examples that generate dropdown menus for bots and files. WIP

## selenium_multi_backtest.py
Behold! Selenium driver is required for this to work. In current verson it creates multiple clones via api, configures them whilst another scrip instance logins via browser and uses backtesting Remote to quickly trigger it for multiple bots at a time.
## init.py
Provides with basic Haasonline server conectivity commands.
## configserver.py
Func script to read and write to config file your server data.
## interval.py
Func script that reads, writes and converts dates into ticks and vice'versa.
## botsellector.py
Stores a Class BotSellector. Gets you specific Trade or Mad Hatter bot, or the list thereof.
## botinterface.py
Was my first attempt at OOP... it can do allmost everything other scripts do and it has some comments. Go check them out.
## botdatabase.py
-Stores/reads bots from/to files
-Bruteforce markets with saved mh_bots as configs.
-Bruteforce markets with configs from a csv file.
-Stores bruteforce backtesting results in a csv.


## history.py
- retrievemarket data from Haas servers
- Store it on disk/sql
- Provides it in DataFrame format for data science.
- Plot multiple trades from multiple backtests on a single graph for better analysis.

Usage examples are provided at the bottom of the script.


