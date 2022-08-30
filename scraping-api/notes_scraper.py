from datetime import datetime
import pandas
import requests
import json
from bs4 import BeautifulSoup
import os
import re
from nltk.tokenize import sent_tokenize
from tqdm import tqdm

patterns = ['fiscal', '$', '[\d]{1,}']

def string_has_revenue(string):
    if string is None: return False
    matcher = 'revenue'
    if matcher in string.lower(): return True
    return False

def string_has_balance(string):
    if string is None: return False
    matcher = 'balance sheets'
    if matcher in string.lower(): return True
    return False

def string_has_assets(string):
    if string is None: return False
    matcher = 'assets'
    if matcher in string.lower(): return True

def string_has_notes(string):
    if string is None: return False
    matcher = 'notes to consolidated financial statements'
    if matcher in string.lower() and len(string) <= len(matcher) + 2: return True
    return False

BASE_URL_CIK = 'https://data.sec.gov/submissions/'
BASE_URL_FORM = 'https://www.sec.gov/Archives/edgar/data/'
DATA_FOLDER = 'data'
RESULT_DIR = 'result'
OPEN_IE_DIR = 'Open-IE'
FILING_DIR = 'json'

companies_list = pandas.read_csv('{}/saas_list.csv'.format(DATA_FOLDER), usecols=['Company'])['Company'].to_list()

cik_df = pandas.read_csv('{}/res.csv'.format(RESULT_DIR), usecols=['name','cik'])

for company in tqdm(companies_list):
    try:
        [record] = cik_df.index[cik_df['name'] == company]
        cik = str(int(cik_df.at[record,'cik']))
        if pandas.isna(cik):
            print("CIK not available")
            continue
        cik = '0'*(10-len(cik)) + cik
        
        url = BASE_URL_CIK + 'CIK' + cik + '.json'
        res = requests.get(url, headers={'user-agent':"xxxx@yyyy.com",'Accept-Encoding':'gzip, deflate, br'})
        data = json.loads(res.text)
        
        recent_filings = data["filings"]['recent']
        accession_no = recent_filings['accessionNumber']
        accepted_on =  recent_filings['acceptanceDateTime'] 
        form_type = recent_filings['form']
        
        scraped_indices = []
        
        for i in range(len(accepted_on)):
            sub_date = datetime.strptime(accepted_on[i],"%Y-%m-%dT%H:%M:%S.%fZ")
            if sub_date<datetime(2020,1,1,0,0):
                break
            if form_type[i]=='8-K' or form_type[i]=='10-K' or form_type[i]=='10-Q':
                scraped_indices.append(i)

        for j in scraped_indices:
            if form_type[j] != '10-K': continue
            url =  BASE_URL_FORM + cik + '/'+ accession_no[j] + '.txt'
            req = requests.get(url, headers={'user-agent':"xxxx@yyyy.com",'Accept-Encoding':'gzip, deflate, br'})
            file_content = req.text
            sub_str1 = file_content.find('<XBRL>')
            sub_str2 = file_content.find('</XBRL>')
            if len(file_content[sub_str1:sub_str2]) <10:
                write_data = file_content
            else:
                write_data = file_content[sub_str1:sub_str2]
            with open('test.txt','w') as f:
                f.write(write_data)
        
            with open("test.txt") as f:
                soup = BeautifulSoup(f.read(),'lxml')
                [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
                text = ''

                try:
                    notes_tag = soup.find('span', string=string_has_balance).find_next('table') \
                            .find_next('td', string=string_has_assets) \
                            .find_next('td', string=string_has_revenue) \
                            .find_next('span', string=string_has_notes)
                    # print(notes_tag)
                    parent_tag = notes_tag.parent.parent
                    # print(parent_tag)
                    idx = 1
                    while idx <= 200:
                        try:
                            sibling = parent_tag.next_sibling
                            text_content = sibling.text
                            text += text_content + '\n'
                            parent_tag = sibling
                            idx += 1
                        except: break

                    if len(text) < 10:
                        file_name = "{}/".format(FILING_DIR)+company +'/'+ form_type[j]+"_"+accepted_on[j][0:10]+".json"
                        with open(file_name, 'r', encoding='utf-8') as file:
                            content = json.load(file)
                        use_key = None
                        for key in content:
                            if 'significantaccountingpolicies' in key.lower():
                                use_key = key
                                break
                        content_ = content[use_key]
                        soup_aux = BeautifulSoup(list(content_.values())[0], 'lxml')
                        text = soup_aux.text
                        with open('test_2.txt', 'w') as file: file.write(text)
                    try:
                        os.makedirs("{}/".format(OPEN_IE_DIR)+company)
                    except:
                        pass
                    file_name = "{}/".format(OPEN_IE_DIR)+company +'/'+ form_type[j]+"_"+accepted_on[j][0:10]+".txt"
                    with open(file_name, 'w') as file:
                        file.write(text)

                    with open(file_name, 'r') as file:
                        text_data = file.read()

                    sents = sent_tokenize(text_data)
                    text = ''
                    for sent in sents:
                        flag_match = False
                        if 'fiscal' in sent.lower(): flag_match = True
                        if '$' in sent: flag_match = True
                        if re.match('[\d]{1,}', sent): flag_match = True
                        if flag_match:
                            text += sent + '\n'

                    with open(file_name, 'w') as file:
                        file.write(text)
                except: pass
    except: continue
