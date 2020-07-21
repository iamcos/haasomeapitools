i_dfs = []
for i in dfs:
    kv_i = []
    for ii in i:
        
        i_dfs.append([type(ii),type(i)])
        
    # print(kv_i)
    i_dfs.append(kv_i)
    

df = pd.DataFrame.from_dict(i_dfs)
for i in df:
    # print(i)
    pass
# print((df.values))

import numpy as np 
df2 = df[0].to_list(),df[1].to_list()
# print(df2)
df3 = []
for i in df2[0]:
    # df3.append(str(i))
    df3.append(str(i))

for i in df2[1]:
    # df3.append(str(i))
    df3.append(str(i))
import numpy as N
res = N.array(df3)
print('res\n\n\n',res,len(res)) 
unique_res = N.unique(res) 
print("Unique elements of the list using numpy.unique():\n")
print((unique_res),len(unique_res))