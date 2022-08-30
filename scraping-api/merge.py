import pandas as pd

RESULT_DIR = 'result'

df1 = pd.read_csv("{}/res1.csv".format(RESULT_DIR)) # res1 file contains the Ticker symbol for each organization with CIK, gathered from data/nasdaq.csv
df1 = df1.drop(['num','symbol'],axis=1)
df1['cik'] = df1['cik'].astype(str)

df2 = pd.read_csv("{}/res2.csv".format(RESULT_DIR)) # res2 file contains the name for each organization with CIK
df2 = df2.drop(['num'],axis=1)
df2['cik'] = df2['cik'].astype(str)

df3 = pd.read_csv("{}/manual.csv".format(RESULT_DIR)) # File containing manually added CIK for organizations, if any
df3 = df3.drop(['num'],axis=1)
df3['cik'] = df3['cik'].astype(str)


res = pd.concat([df1,df2,df3],ignore_index=True)
res.sort_values('name', ascending=True)
res['cik'] = res['cik'].astype(str)
print(res.shape)
res.to_csv('{}/res.csv'.format(RESULT_DIR)) # Merging the data into one CSV for later use
