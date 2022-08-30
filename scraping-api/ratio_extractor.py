from glob import glob
import json
import os
from datetime import datetime
import pandas
from tqdm import tqdm
import yfinance as yf
from urllib import request
from bs4 import BeautifulSoup as BS

pe_ratio = {}
pm_ratio = {}

revenue = {}
marketing = {}

sprice = {}
eps = {}

DATE_PATTERN = '%Y-%m-%d'
FILE_TYPE = '10-K'
info_db = pandas.read_csv('result/res1.csv')

def get_data(url, trading_symbol):
    content = request.urlopen(url)
    soup = BS(content, 'lxml')
    data = {}
    data['price'] = soup.find('fin-streamer', {'data-symbol': trading_symbol}).text
    return data

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

# Parses the relevant fields from each Earnings per share data point
def parse_eps_data(values):
    start_date_ = values['period']['startDate']
    end_date_ = values['period']['endDate']

    start_date = datetime.strptime(start_date_, DATE_PATTERN)
    end_date = datetime.strptime(end_date_, DATE_PATTERN)

    num_months = diff_month(end_date, start_date)
    if num_months < 10 or diff_month(datetime.now(), start_date) > 18: return False
    return (start_date_, end_date_), values['value']

# Parses the relevant fields from each Marketing Costs data point
def parse_marketing_costs(values):
    start_date_ = values['period']['startDate']
    end_date_ = values['period']['endDate']

    start_date = datetime.strptime(start_date_, DATE_PATTERN)
    end_date = datetime.strptime(end_date_, DATE_PATTERN)

    num_months = diff_month(end_date, start_date)
    if num_months < 10: return False
    return (start_date_, end_date_), values['value']

# Parses the relevant fields from each Revenue data point
def parse_revenues(values):
    start_date_ = values['period']['startDate']
    end_date_ = values['period']['endDate']

    start_date = datetime.strptime(start_date_, DATE_PATTERN)
    end_date = datetime.strptime(end_date_, DATE_PATTERN)

    num_months = diff_month(end_date, start_date)
    if num_months < 10: return False
    if 'value' not in values: return False
    return (start_date_, end_date_), values['value']

for company in tqdm(os.listdir('json')):
    try:
        for file_name in glob('json/{}/{}*'.format(company, FILE_TYPE)):
            with open(file_name, 'r', encoding='utf-8') as file:
                data = json.load(file)

            default_key = 'StatementsOfIncome'
            if default_key not in data: default_key = 'StatementsOfComprehensiveIncome'

            default_key2 = 'SellingAndMarketingExpense'
            if default_key2 not in data[default_key]: default_key2 = 'SellingGeneralAndAdministrativeExpense'
            if default_key2 not in data[default_key]: default_key2 = 'GeneralAndAdministrativeExpense'

            default_key_ = ['StatementsOfIncome', 'StatementsOfComprehensiveIncome', 'DisclosureBASICANDDILUTEDNETLOSSPERSHAREScheduleOfBasicAndDilutedNetLossPerCommonShareDetails']
            default_key3 = ['EarningsPerShareBasic', 'EarningsPerShareBasicAndDiluted']
            flag_found = False
            for df_ in default_key_:
                if df_ not in data: continue
                for df3_ in default_key3:
                    if df3_ not in data[df_]: continue
                    default_key_eps = df_
                    default_key_eps3 = df3_
                    flag_found = True 
                    break
                if flag_found: break

            # Revenue collector
            statements_of_income = data[default_key]
            for type_revenue, values in statements_of_income.items():
                if 'revenue' not in type_revenue.lower(): continue
                for value in values:
                    item = parse_revenues(value)
                    if not item: continue

                    if company not in revenue: revenue[company] = {}
                    revenue[company]['SEP'.join(item[0])] = item[1]

            # Marketing collector
            marketing_data = data[default_key][default_key2]
            for values in marketing_data:
                item = parse_marketing_costs(values)
                if not item: continue

                if company not in marketing: marketing[company] = {}
                marketing[company]['SEP'.join(item[0])] = item[1]

            # Earnings per share collector
            eps_data = data[default_key_eps][default_key_eps3]
            for values in eps_data:
                item = parse_eps_data(values)    
                if not item: continue

                if company not in eps: eps[company] = {}
                eps[company]['SEP'.join(item[0])] = item[1]

            # Share price collector
            if company in sprice: continue
            trading_symbol = info_db.loc[info_db['name'] == company, 'symbol']
            if len(trading_symbol) == 0: continue
            trading_symbol = list(trading_symbol)[0]
            data = yf.download(trading_symbol, '2022-03-19', '2022-03-19')
            price = data['Close'].values[0]
            sprice[company] = price

    except Exception as exp:
        with open('error.txt', 'a') as file:
            file.write(company + '\n')


with open('revenue_{}.json'.format(FILE_TYPE), 'w') as file:
    json.dump(revenue, file)

with open('marketing_{}.json'.format(FILE_TYPE), 'w') as file:
    json.dump(marketing, file)

with open('earnings_per_share_{}.json'.format(FILE_TYPE), 'w') as file:
    json.dump(eps, file)

with open('share_price.json', 'w') as file:
    json.dump(sprice, file)

with open('revenue_{}.json'.format(FILE_TYPE), 'r') as file:
    revenue = json.load(file)

with open('marketing_{}.json'.format(FILE_TYPE), 'r') as file:
    marketing = json.load(file)

with open('earnings_per_share_{}.json'.format(FILE_TYPE), 'r') as file:
    eps = json.load(file)

with open('share_price.json', 'r') as file:
    sprice = json.load(file)
    
for company in tqdm(marketing):
    try:
        for m_date in marketing[company]:
            r_value = revenue[company][m_date]
            if company not in pm_ratio: pm_ratio[company] = {}
            pm_ratio[company][m_date] = float(r_value)/float(marketing[company][m_date])
    except:
        with open('errors_.txt', 'a') as file:
            file.write(company + '\n')

for company in tqdm(eps):
    try:
        eps_val = list(eps[company].values())[0]
        price = sprice[company]
        pe_ratio[company] = float(price) / float(eps_val)
    except:
        with open('errors_.txt', 'a') as file:
            file.write(company + '\n')

with open('pm_ratio.json', 'w') as file:
    json.dump(pm_ratio, file)

with open('pe_ratio.json', 'w') as file:
    json.dump(pe_ratio, file)
