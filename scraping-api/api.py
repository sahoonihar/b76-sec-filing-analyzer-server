from datetime import datetime
import os
from sec_api import XbrlApi
import pandas 
import requests
import json
import random
from tqdm import tqdm

BASE_URL_CIK = 'https://data.sec.gov/submissions/'
# API Key, generate by signing up at sec-api.io
API_KEY = "bc91833a1bf76a681a9605b479eaXXXXXXXXXXXXXXd4a6e"
DATA_FOLDER = 'data'
RESULT_DIR = 'result'
OUTPUT_DIR = 'json'
TILL_YEAR = 2020 # Change this to 2017 if you want to fetch all files on or after 1st Jan, 2017

# Using the sec-api to fetch the XBRL data
xbrlApi = XbrlApi(api_key=API_KEY)

# saas_list.csv contains the list of saas orgs in a csv file
companies_list = pandas.read_csv('{}/saas_list.csv'.format(DATA_FOLDER), usecols=['Company'])['Company'].to_list()

cik_df = pandas.read_csv('{}/res.csv'.format(RESULT_DIR), usecols=['name','cik'])

for company in tqdm(companies_list):
    [record] = cik_df.index[cik_df['name'] == company]
    try: cik = str(int(cik_df.at[record,'cik']))
    except: 
        print('here')
        continue
    if pandas.isna(cik):
        print("CIK not available")
        continue
    cik = '0'*(10-len(cik)) + cik
    
    url = BASE_URL_CIK + 'CIK' + cik + '.json'
    # Specify a valid user agent, else response is a 403 code
    res = requests.get(url, headers={'user-agent':"xxxx@yyyy.com",'Accept-Encoding':'gzip, deflate, br'})
    data = json.loads(res.text)
    
    recent_filings = data["filings"]['recent']
    accession_no = recent_filings['accessionNumber']
    accepted_on =  recent_filings['acceptanceDateTime'] 
    form_type = recent_filings['form']
    
    scraped_indices = []
    
    for i in range(len(accepted_on)):
        sub_date = datetime.strptime(accepted_on[i],"%Y-%m-%dT%H:%M:%S.%fZ")
        # Limiting the look-back to only two years
        if sub_date<datetime(TILL_YEAR,1,1,0,0):
            break
        if form_type[i]=='10-K' or form_type[i]=='10-Q':
            scraped_indices.append(i)
    
    for i in scraped_indices:
        xbrl_json = xbrlApi.xbrl_to_json(accession_no=accession_no[i])
        try:
            os.makedirs("{}/"+company.OUTPUT_DIR)
        except:
            pass
        filename = "{}/".format(OUTPUT_DIR) + company + '/' + form_type[i] + "_" + accepted_on[i][0:10] + ".json"
        while os.path.exists(filename):
            filename = "{}/".format(OUTPUT_DIR) + company + '/' + form_type[i] + "_" + accepted_on[i][0:10] + "_" + str(random.randrange(1,10)) + ".json"
 
        with open(os.path.join(filename),'x',encoding="utf-8") as m:
             json.dump(xbrl_json,m, indent=4)   
