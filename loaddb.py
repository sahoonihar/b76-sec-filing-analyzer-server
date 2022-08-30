import json
import sys
import os
import config
from pymongo import MongoClient
import csv

db = MongoClient()[config.DBNAME]

data_dir = sys.argv[1]

with open(os.path.join(data_dir,'cik_name_mapping.csv')) as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        row[2] = '0'*(10 - len(str(row[2]))) + str(row[2])
        cik_file_path = os.path.join(data_dir,f"financial-data/{row[2]}.json")
        name_file_path = os.path.join(data_dir,f"company-data/{row[1]}.json")
        if os.path.exists(cik_file_path):
            print(cik_file_path)
            try:
                data_dict = json.loads(open(cik_file_path).read())
                data_dict['Filings'] = json.loads(open(name_file_path).read())['filings']
                data_dict['Name'] = row[1]
            except:
                continue
            db['company_data'].insert_one({'cik' : row[2], 'data' : data_dict})
