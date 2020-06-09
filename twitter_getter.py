import twitter_scraper as tw
import pandas as pd
from multiprocessing import Pool, TimeoutError
import multiprocessing as mp
import time
import pandas as pd
import numpy as np
import requests
import multiprocessing as mp
import os
class CryptoTweets:
    def __init__(self):
        self.t = tw


    def get_tweets_single_process(self, acc, pages=1):

        tweets = [x for x in self.t.get_tweets(acc, pages)]
        cols = list(tweets[0].keys())
        # print(
        db2 = pd.DataFrame(tweets, columns=cols)
        return db2
    # accs = ['ExchangeDog']

    def get_tweets(self, accs, pages=1):
    # db = pd.DataFrame(columns = cols)
        dfs = []
        for acc in accs:
            tweets = [x for x in self.t.get_tweets(acc,pages)]
            cols = list(tweets[0].keys())
            # print(
            db2 = pd.DataFrame(tweets,columns=cols)
            dfs.append(db2)
        result = pd.concat(dfs, ignore_index=True)
        result['time'] = pd.to_datetime(result['time'])

        result.sort_values(by='time', ascending=False, inplace=True)
        result.sort_index(axis=0,inplace=True)
        # dfs.append(db2)
        # print(db2)
        # print(result)

        # filename = [f'{[i for i in accs]}.csv']
        try:
            tweets = pd.read_csv('tweets.csv')
            # print(tweets)
            result2 = pd.concat([tweets,result], ignore_index=True).drop_duplicates().sort_values(by='time',ascending=True,inplace=True).sort_index(axis=0,inplace=True)
            result2.to_csv('tweets.csv')
            # print(result2)
            return result2
        except:
            result.to_csv('tweets.csv')
            # print(result)
            return result



def parallelize_dataframe(func, accs, num_partitions,num_workers):
        pool = mp.Pool(num_workers)
        df = pd.concat(pool.map(func, accs))
        df['time'] = pd.to_datetime(df['time'])
        pool.close()
        pool.join()
        df.sort_values(by='time', ascending=False, inplace=True)
        df.sort_index(axis=0, inplace=True)
        return df

def signals_csv(csv):
    df = pd.read_csv(csv)
    df2 = pd.DataFrame(df.text,columns=['text','labels'])
    # df = df[text
    df2.to_csv('tweets_signals.csv')
    print(df2)


def signals_json(csv):
    df = pd.read_csv(csv)
    df2 = pd.DataFrame(df.text, columns=['text', 'labels'])
    # df = df[text
    df2.to_json('tweets_signals.json',orient='records')
    print(df2)
def to_text(csv):
    df = pd.read_csv(csv)
    with open('signals.txt', 'a') as f:
        p = []
        for i in range(0,df.index.max()):
            f.write(df.text[i])

def main():


 # num_workers = 4
    # tweets
    # accs = ['ExchangeDog', 'Whale_Sniper', 'FishTheWhales',
        # 'BinancePlusPlus', 'bitpeaks', 'ArbingTool']
    # num_partitions = len(accs)
    # t = CryptoTweets().get_tweets(accs,pages=20)
    # df = parallelize_dataframe(CryptoTweets().get_tweets(accs), accs, num_partitions, num_workers)
    # print(t)
    to_text('tweets.csv')
    # return t

if __name__ == "__main__":
    main()
