import pandas as pd

df = pd.read_json('current_bot.csv')

columns = list(df.columns)
columns.append('ordersCount')

# df.columns = columns
# print(df.columns)
df['ordersCount'] = None
for i in df.index:
    df['ordersCount'][i] = len(df.completedOrders[i])
# print(df[['roi','macd','rsi','bBands','interval','ordersCount']])
df.sort_values(['roi'],inplace=True)
# print(


df3 = pd.DataFrame()
df2 = df[['roi','macd','rsi','bBands','interval','ordersCount']]
dfs = []

for i,b in df2.rsi.items():
    # print(i,b)
    for a,c in b.items():
        try: 
            for x,z in c.items():
                dfs.append([i,b,a,c,x,z])
    
        except Exception as e:
            # print(e)
            pass
print(len(dfs))
print(type(dfs))
dfs_keys = []
dfs_set = []
# print((dfs_set))
for i in dfs[0:-1]:
    dfs_keys.append(str(i))
    for b in i[0:-1]:
        dfs_set.append(str(b))
import numpy as N
res = N.array(dfs_set)
unique_res = N.unique(res)
print('res\n\n\n LENGTH',len(res),'LENGTH 2 ',len(unique_res)) 
 
# print(dfs_keys)
res = N.array(dfs_keys)
unique_res = N.unique(res)
print('res\n\n\n LENGTH',len(res),'LENGTH 2 ',len(unique_res)) 
# print(set(unique_res))
dicts=[]
for i in set(unique_res):
    b = i.split(' , ')
    for ii in b:
        iii = ii.replace('[', "")
        iii = ii.replace('[', "")
        iii = ii.replace(']','')
        iii = ii.replace('}','')
        iii = ii.replace('}','')
        iii = ii.replace('"',"")
        iii = ii.replace(' " ',"")
        iv = iii.split(',')
        # print(set(iv))
        # print([i.split('') for i in iv[3:5]])
        # for iv in i?v)
# print(pd.DataFrame(dicts))
ref = []
for i in df.columns:
    try:
        reform = {(outerKey, innerKey): values for outerKey, innerDict in df[i].items() for innerKey, values in innerDict.items()}
        for v in ['RsiLength', 'RsiOversold', 'RsiOverbought', 'MacdFast', 'MacdSlow', 'MacdSign','Length', 'Devup', 'Devdn', 'MaType', 'Deviation', 'ResetMid', 'AllowMidSell', 'RequireFcc', 'Interval']:
            for i,ii in reform.items():
                if i[ii][v]:
                    print(i)
                    

                ref.append(reform)
                print(reform)
       
    except Exception as e:
        # print(e)
        pass

