import os

import pandas as pd

gvlab_dataset_path = '/Users/yonatab/PycharmProjects/GVLAB-MTURK/gvlab/created_data/user_collected_associations_qualification.csv'
solve_url = 'https://gvlab-dataset.github.io/mturk/solve'

if __name__ == '__main__':
    df = pd.read_csv(gvlab_dataset_path)
    print(f"Read df: {len(df)}")
    df = df.sample(frac=1)
    solve_urls = df['annotation_index'].apply(lambda x: f"{solve_url}/solve_create_qualification_{x}")
    solve_urls.to_csv(os.path.join('urls', 'urls_solve_create_qual.csv'), index=False)
    print("Done")