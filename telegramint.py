from parse import compile
from pyrogram import Filters
from pyrogram import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client
from parse import *
import re
app = Client("my_account")

buy = re.compile(r'BUY*\w', re.IGNORECASE)
sell = re.compile(r'Sell\s*\w', re.IGNORECASE)
buying_activity = re.compile(r'BUYING activity', re.IGNORECASE)
selling_activity = re.compile(r'SELLING activity', re.IGNORECASE)
market_identification = re.compile(r'market',re.IGNORECASE)
@app.on_message(Filters.chat(['SignalsFromCryptoJournal','whynotmake']))
def recieve_updates(client, message):
    buy_signal = []
    text = message.text.split('\n')
    for i in text:
        # print(i)
        if buy.parse(i):
            buy_signal.append(buy.parse(i)[0])
        # print
    print(buy_signal)

@app.on_message(Filters.chat(['SignalsFromCryptoJournal', 'whynotmake']))
def recive_updates(client, message):
    text = message.text
    for i in text:
        if

app.run()
