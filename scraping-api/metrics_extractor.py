from glob import glob
import json
import os
from tqdm import tqdm
from datetime import datetime

DATE_PATTERN = '%Y-%m-%d'

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

# Parses the relevant fields from each income data point
def parse_income_data(values):
    start_date_ = values['period']['startDate']
    end_date_ = values['period']['endDate']

    start_date = datetime.strptime(start_date_, DATE_PATTERN)
    end_date = datetime.strptime(end_date_, DATE_PATTERN)

    num_months = diff_month(end_date, start_date)
    if num_months < 10 or diff_month(datetime.now(), start_date) > 18: return False
    return (start_date_, end_date_), values['value']

# Parses the relevant fields from each depreciation and amortization data point
def parse_ebitda_data(values):
    start_date_ = values['period']['startDate']
    end_date_ = values['period']['endDate']

    start_date = datetime.strptime(start_date_, DATE_PATTERN)
    end_date = datetime.strptime(end_date_, DATE_PATTERN)

    num_months = diff_month(end_date, start_date)
    if num_months < 10 or diff_month(datetime.now(), start_date) > 18: return False
    if 'value' not in values: return False
    return (start_date_, end_date_), values['value']

# Parses the income pertaining to EBIT
def parse_ebit_data(values):
    start_date_ = values['period']['startDate']
    end_date_ = values['period']['endDate']

    start_date = datetime.strptime(start_date_, DATE_PATTERN)
    end_date = datetime.strptime(end_date_, DATE_PATTERN)

    num_months = diff_month(end_date, start_date)
    if num_months < 10 or diff_month(datetime.now(), start_date) > 18: return False
    return (start_date_, end_date_), values['value']

# Parses assets that an organization has, from the last 18 months
def parse_asset_data(values):
    end_date_ = values['period']['instant']

    end_date = datetime.strptime(end_date_, DATE_PATTERN)

    if diff_month(datetime.now(), end_date) > 18: return False
    return end_date_, values['value']

# Parses liabilities that an organization has, from the last 18 months
def parse_liabilities_data(values):
    end_date_ = values['period']['instant']

    end_date = datetime.strptime(end_date_, DATE_PATTERN)

    if diff_month(datetime.now(), end_date) > 18: return False
    return end_date_, values['value']
    
# Computes the ROCE using the latest data points - EBIT, Assets and Liabilities
def get_roce_data(assets, liabilities, ebit):
    most_recent_instant = None
    for key in set(list(assets.keys()) + list(liabilities.keys())):
        key_date = datetime.strptime(key, DATE_PATTERN)
        if diff_month(datetime.now(), key_date) < 12:
            most_recent_instant = key
            break

    ebit_key = None
    for key in ebit.keys():
        key_date = datetime.strptime(key.split('SEP')[-1], DATE_PATTERN)
        if diff_month(datetime.now(), key_date) < 12:
            ebit_key = key
            break

    return float(ebit[ebit_key]) / (float(assets[most_recent_instant]) - float(liabilities[most_recent_instant]))

ebit = {}
ebitda = {}

assets = {}
liabilities = {}

net_income = {}
share_equity = {}

roce = {}

for company in tqdm(os.listdir('json')):
    try:
        for file_name in glob('json/{}/10-K*'.format(company)): # Computing the values from 10-K only
            operating_expenses = {}
            with open(file_name, 'r', encoding='utf-8') as file:
                    data = json.load(file)

            # EBIT extractor
            default_key_vals = ['StatementsOfIncome', 'StatementsOfComprehensiveIncome'] # Choosing on from different un-normalized possibilties
            for df in default_key_vals:
                if df in data:
                    default_key = df
                    break
            default_key_ebit = 'OperatingIncomeLoss'
            values = data[default_key][default_key_ebit]
            for value in values:
                item = parse_ebit_data(value)
                if not item: continue

                if company not in ebit: ebit[company] = {}
                ebit[company]['SEP'.join(item[0])] = item[1]
                operating_expenses['SEP'.join(item[0])] = item[1]

            # EBITDA extractor
            default_key2 = 'StatementsOfCashFlows'
            default_key_ebitda_vals = ['DepreciationDepletionAndAmortization', 'Depreciation', \
                'DepreciationAndAmortization', 'DepreciationDepletionAndAmortizationExcludingAmortizationOfDeferredContractCosts', \
                    'OtherDepreciationAndAmortization', 'DeprecationDepletionAndAmortizationExcludingAmortizationOfDeferredSalesCommissions']
            for df_ebtda in default_key_ebitda_vals:
                if df_ebtda in data[default_key2]: 
                    default_key_ebitda = df_ebtda
                    break

            values = data[default_key2][default_key_ebitda]
            for value in values:
                item = parse_ebitda_data(value)
                if not item: continue

                if company not in ebitda: ebitda[company] = {}
                ebitda[company]['SEP'.join(item[0])] = operating_expenses['SEP'.join(item[0])] + item[1]

            # ROCE
            # Assets extractor
            default_key3 = 'BalanceSheets'
            default_key_asset = 'Assets'
            values = data[default_key3][default_key_asset]
            for value in values:
                item = parse_asset_data(value)
                if not item: continue

                if company not in assets: assets[company] = {}
                assets[company][item[0]] = item[1]   

            # Liabilities extractor
            default_key3 = 'BalanceSheets'
            default_key_asset = 'LiabilitiesCurrent'
            values = data[default_key3][default_key_asset]
            for value in values:
                item = parse_asset_data(value)
                if not item: continue

                if company not in liabilities: liabilities[company] = {}
                liabilities[company][item[0]] = item[1]

            if company not in assets or company not in liabilities or company not in ebit: continue
            roce[company] = get_roce_data(assets[company], liabilities[company], ebit[company]) * 100

    except:
        # Noting organizations which resulted in some error - to improve recall
        with open('error.log', 'a') as file:
            file.write(company + '\n')

with open('ebit.json', 'w') as file:
    json.dump(ebit, file)

with open('ebitda.json', 'w') as file:
    json.dump(ebitda, file)

with open('roce.json', 'w') as file:
    json.dump(roce, file)
