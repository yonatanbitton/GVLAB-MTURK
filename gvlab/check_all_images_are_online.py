import json

import boto3
import pandas as pd

p = '/Users/yonatab/PycharmProjects/GVLAB-backend/assets/gvlab_dataset.csv'
session = boto3.Session()
s3 = session.resource('s3')

data = s3.Bucket('gvlab-bucket')
all_keys = []
for my_bucket_object in data.objects.all():
    all_keys.append(my_bucket_object.key.split(".")[0])

df = pd.read_csv(p)
df['candidates'] = df['candidates'].apply(json.loads)

all_candidates = []
for c_lst in df['candidates'].values:
    all_candidates += c_lst
all_candidates_set = set(all_candidates)

print(f"s3_keys: {len(all_keys), len(set(all_keys))}, all_candidates_set: {len(all_candidates_set)} (lst: {len(all_candidates)})")
all_keys_set = set(all_keys)

in_s3_but_not_in_candidates = len(all_keys_set.difference(all_candidates_set))
in_candidates_but_not_in_s3 = len(all_candidates_set.difference(all_keys_set))
intersection_s3_candidates = len(all_candidates_set.intersection(all_keys_set))
print(f"in_s3_but_not_in_candidates: {in_s3_but_not_in_candidates}")
print(f"in_candidates_but_not_in_s3: {in_candidates_but_not_in_s3}")
print(f"intersection_s3_candidates: {intersection_s3_candidates}")

print("Done")