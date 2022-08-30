import json
import sys
from collections import defaultdict
import csv

sentiment_dict = defaultdict(lambda : defaultdict(lambda:defaultdict(dict)))

keys = "fog_idx,pos_score,neg_score,polarity_score,uncertain_score,constrain_score,lit_score,interesting_score,pos_word_prop,neg_word_prop,uncertain_word_prop,constrain_word_prop,lit_word_prop,interesting_word_prop".split(",")
with open(sys.argv[1]) as f:
    reader = csv.DictReader(f)
    for row in reader:
        sentiment_dict[row["cik"]][row["type"]][row["date"]] = {key : row[key] for key in keys}

print(json.dumps(sentiment_dict))