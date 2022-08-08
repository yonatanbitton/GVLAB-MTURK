import json
import os

import pandas as pd


def get_json(file_path):
    with open(os.path.join(file_path)) as f:
        response = json.load(f)
        f.close()
        return response

base_url = 'https://gvlab-bucket.s3.amazonaws.com/{}'
# base_url = 'https://winogavil.s3.eu-west-1.amazonaws.com/{}'
image_cue_pairs = get_json(r'C:\devel\GVLAB-MTURK\association_category_type\pairs_to_annotate.json')
count = 0
def create_batch(batch, batch_number):
    global count
    for pair in batch:
        pair.update({'image_url': base_url.format(pair['image'])})
        count += 1
    pd.DataFrame(batch).to_csv(r'.\winogavil-pairs-{}.csv'.format(batch_number), encoding='utf-8', index=False)

zero_batch = []
for pair in image_cue_pairs[:100]:
    zero_batch.append(pair)
create_batch(zero_batch, 0)

first_batch = []
for pair in image_cue_pairs[100:200]:
    first_batch.append(pair)
create_batch(first_batch, 1)

second_batch = []
for pair in image_cue_pairs[200:300]:
    second_batch.append(pair)
create_batch(second_batch, 2)

third_batch = []
for pair in image_cue_pairs[300:400]:
    third_batch.append(pair)
create_batch(third_batch, 3)

forth_batch = []
for pair in image_cue_pairs[400:500]:
    forth_batch.append(pair)
create_batch(forth_batch, 4)

fifth_batch = []
for pair in image_cue_pairs[500:1000]:
    fifth_batch.append(pair)
create_batch(fifth_batch, 5)

six_batch = []
for pair in image_cue_pairs[1000:1100]:
    six_batch.append(pair)
create_batch(six_batch, 6)

print(count)