# Import libraries
import json
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

from multiprocessing import Pool

import match_pairs
from spacy.lang.en import English   

def get_ideas(market='binance', pages=5):

    ideas = []
    for i in range(1, pages):
        if i == 0: 
            pass
        elif i >= 1:
            page = requests.get(
                f"https://www.tradingview.com/ideas/search/{market}/page-{i}/?sort=recent")
            soup = BeautifulSoup(page.text, 'lxml')

            cards = soup.find_all(
                'div', {'class': 'tv-feed__item js_cb_class tv-feed-layout__card-item'})
            cards_content = soup.find_all(
                'p', {'class': 'tv-widget-idea__description-row tv-widget-idea__description-row--clamped js-widget-idea__popup'})
            cards_time = soup.find_all(
                'span', {'class': 'tv-card-stats__time js-time-upd'})
            move_dir = soup.find_all(
                'span', {'class': re.compile('tv-idea-label tv-widget-idea__label tv-idea-label--*')})
            # print(move_dir)
            # for i in cards_time:
            #     print(i['data-timestamp'])
            for card, card1,time,move in zip(cards, cards_content,cards_time,move_dir):

                data = json.loads(card['data-card'])
                data['data']['text'] = card1.text.replace("\n"," ").replace("\t","  ")
                data['data']['time'] = pd.to_datetime(time['data-timestamp'],unit='s')
                data['data']['author'] = data['author']['username']
                data['data']['move'] = move.text.replace("\n"," ").replace(" ","")
                


                del data['author']
                del data['data']['base_url']
                del data['data']['image_url']
                del data['data']['is_public']
                del data['data']['is_script']
                del data['data']['published_url']
                ideas.append(data)
            dfs = []
            for i,ii in enumerate(ideas):
                dic = {(level1_key, level2_key): values for level1_key, level2_dict in ii.items() for level2_key, values in level2_dict.items()}
                d = pd.DataFrame(dic,index=[i])
                dfs.append(d)
            df = pd.concat(dfs)


    return df

def parse(url):

            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'lxml')

            cards = soup.find_all(
                'div', {'class': 'tv-feed__item js_cb_class tv-feed-layout__card-item'})
            cards_content = soup.find_all(
                'p', {'class': 'tv-widget-idea__description-row tv-widget-idea__description-row--clamped js-widget-idea__popup'})
            cards_time = soup.find_all(
                'span', {'class': 'tv-card-stats__time js-time-upd'})
            move_dir = soup.find_all(
                'span', {'class': re.compile('tv-idea-label tv-widget-idea__label tv-idea-label--*')})
            # print(move_dir)
            # for i in cards_time:
            #     print(i['data-timestamp'])
            ideas = []
            for card, card1,time,move in zip(cards, cards_content,cards_time,move_dir):

                data = json.loads(card['data-card'])
                data['data']['text'] = card1.text.replace("\n"," ").replace("\t","  ")
                data['data']['time'] = pd.to_datetime(time['data-timestamp'],unit='s')
                data['data']['author'] = data['author']['username']
                data['data']['move'] = move.text.replace("\n"," ").replace(" ","")
                


                del data['author']
                del data['data']['base_url']
                del data['data']['image_url']
                del data['data']['is_public']
                del data['data']['is_script']
                del data['data']['published_url']
                ideas.append(data)
            dfs = []
            for i,ii in enumerate(ideas):
                dic = {(level1_key, level2_key): values for level1_key, level2_dict in ii.items() for level2_key, values in level2_dict.items()}
                d = pd.DataFrame(dic,index=[i])
                dfs.append(d)
            df = pd.concat(dfs)


            return df

def url():
    urls = []
    try:
        df = pd.read_csv('/Users/cosmos/Documents/GitHub/haasomeapitools/ml_dataset/Binance.300.script.csv')
        pairs = df['short_name'].unique()
        print(pairs)
        for i in pairs:
            url = f'https://www.tradingview.com/symbols/{i}/ideas/?sort=recent'
            urls.append(url)
            for ii in range(2,56):
                url = f'https://www.tradingview.com/symbols/{i}/ideas/page-{ii}/?sort=recent'
                urls.append(url)
        # print(urls)
    except:
        pass
    return urls

def get_ideas2(market='binance', pages=5):

    ideas = []
    for i in range(1, pages):
        if i == 0:
            pass
        elif i >= 1:
            page = requests.get(
                f"https://www.tradingview.com/ideas/search/{market}/page-{i}/?sort=recent").text
            soup = BeautifulSoup(page, 'lxml')
            cards_cont = soup.find('div',{'class':'tv-card-container__main'})
            cards2 = soup.find_all(name='div',attrs={'class':'tv-card-container__main'})
            for i in cards2:
                print(i.text)
            # for i in cards_cont:
                # cards.append(i.find_all('div',{'class':'tv-widget-idea js-userlink-popup-anchor'}))
                
            # cards1 = cards_cont.find_all('div')
            # for i in cards1:
                # print(i.attrs)
            
            # print(cards_cont.attrs)
    #         d = cards_cont.find_all('div',{'class': ['tv-feed__item', 'js_cb_class', 'tv-feed-layout__card-item'
    # ]})     
    #         for i in d:
    #             print(i.attrs)
            # print(d.attrs)
            # cards = soup.find_all(
            #     'div', {'class': ['tv-feed__item js_cb_class tv-feed-layout__card-item',]})
            # css=a.tv-widget-idea__title.apply-overflow-tooltip.js-widget-idea__popup
            #css=div.tv-feed__item.js_cb_class.tv-feed-layout__card-item.js-feed__item--inited
            
def tokenize_ta(text):
    nlp = English()
    my_doc=nlp(text)

    token_list = []
    for token in my_doc:
        token_list.append(token.text)

    return token_list

def main():
    # df = get_ideas2(pages=2)
    urls = url()
    with Pool(10) as p:
    
        records = p.map(parse, urls)
        df = pd.concat(records)

    print(df)
    df['data'].to_csv('ml_dataset/Crypto.56.script.csv')
    # for i in df.index:
    #     with open(f'ml_dataset/{df.data.id.iloc[i]}.txt', 'w') as f:
    #         f.write(df.data.text.iloc[i])
    # print(df)
    
if __name__ == '__main__':
    main()
