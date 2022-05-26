import os
import random

import pandas as pd
import json

gvlab_dataset_path = '/Users/yonatab/PycharmProjects/GVLAB-backend/assets/gvlab_dataset.csv'
gvlab_random_dataset_path = '/Users/yonatab/PycharmProjects/GVLAB-backend/assets/gvlab_dataset_random_10_12_candidates.csv'
create_url = 'https://gvlab-dataset.github.io/mturk/create'
inappropriate_path = '/Users/yonatab/Downloads/to overview'
words_to_filter = [os.path.splitext(img)[0] for img in os.listdir(inappropriate_path)] + ['vibrator']

if __name__ == '__main__':
    df = pd.read_csv(gvlab_dataset_path)
    print(f"Read df: {len(df)}")
    df = df.sample(frac=1)
    df['candidates'] = df['candidates'].apply(json.loads)
    all_images = []
    for C in df['candidates']:
        all_images += C
    all_images_lst = set(all_images)
    all_images_lst_len = len(all_images_lst)
    all_images_lst = [x for x in all_images_lst if x not in words_to_filter]
    print(f'Filtered inappropriate: {all_images_lst_len}->{len(all_images_lst)}')
    df['original_candidates'] = df['candidates']

    rand_cands = []
    for idx, (r_idx, r) in enumerate(df.iterrows()):
        sample_num = 10 if idx % 2 == 0 else 12
        curr_rand_cands = random.sample(all_images_lst, sample_num)
        rand_cands.append(curr_rand_cands)
    df['candidates'] = rand_cands
    create_urls = df['ID'].apply(lambda x: f"{create_url}/random_10_12_candidates_{x}")
    for c in ['original_candidates', 'candidates']:
        df[c] = df[c].apply(json.dumps)
    assert len(set(df['ID'])) == len(df)
    df.to_csv(gvlab_random_dataset_path, index=False)
    print(f'Wrote dataframe of len {len(df)} to {gvlab_random_dataset_path}')
    create_urls.to_csv(os.path.join('urls','urls_create_random_10_12_candidates.csv'),index=False)
    print(f"Wrote URLs CSV: urls_create_random_10_12_candidates.csv")
    print("Done")