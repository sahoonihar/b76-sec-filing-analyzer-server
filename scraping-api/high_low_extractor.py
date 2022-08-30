import yfinance as yf
import pandas
from tqdm import tqdm
import os
import json

# Base dir to get all the meta data - CIK, Ticker symbol
RESULT_DIR = 'result'
START_DATE = '2021-03-20'
END_DATE = '2022-03-19'

info_db = pandas.read_csv('{}/res1.csv'.format(RESULT_DIR))

high_low = {}

for company in tqdm(os.listdir('json')):
    trading_symbol = info_db.loc[info_db['name'] == company, 'symbol']
    if len(trading_symbol) == 0: continue # If no trading symbol, skip
    trading_symbol = list(trading_symbol)[0]
    # Using the yfinance API to get the relevant data
    data = yf.download(trading_symbol, START_DATE, END_DATE)

    high_low[company] = {}
    high_low[company]['high'] = max(data['High'])
    high_low[company]['low'] = max(data['Low'])

with open('high_low.json', 'w') as file:
    json.dump(high_low, file)