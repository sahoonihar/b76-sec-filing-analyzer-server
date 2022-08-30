import yfinance as yf
import pandas
from tqdm import tqdm
import os
import json

# Base dir to get all the meta data - CIK, Ticker symbol
RESULT_DIR = 'result'

info_db = pandas.read_csv('{}/res1.csv'.format(RESULT_DIR))

company_details = {}

for company in tqdm(os.listdir('json')):
    trading_symbol = info_db.loc[info_db['name'] == company, 'symbol']
    if len(trading_symbol) == 0: continue
    trading_symbol = list(trading_symbol)[0]
    # The ticker object contains meta data for an organization
    data = yf.Ticker(trading_symbol)
    
    company_info = data.info
    company_details[company] = {}

    # Getting the business summary (what it does), market cap and dividend yield
    company_details[company]['summary'] = company_info['longBusinessSummary']
    company_details[company]['market_cap'] = company_info['marketCap']
    company_details[company]['dividend_yield'] = company_info['dividendYield']


with open('company_details.json', 'w') as file:
    json.dump(company_details, file)