temimport os
import numpy as np
import pandas as pd

get = "python detection_engine.py --top_n 5 --min_volume 500 --data_granularity_minutes 60 --history_to_use 14 --is_load_from_dictionary 0 --data_dictionary_path 'dictionaries/feature_dict.npy' --is_save_dictionary 1 --is_test 0 --future_bars 5  --data_source binance --stock_list cryptos.txt"

def get_spikes():
    os.system(get)

def open_dict():
    d = np.load('./dictionaries/sample_dict.npy',allow_pickle=True)
    print(help(d))

da = get_spikes()