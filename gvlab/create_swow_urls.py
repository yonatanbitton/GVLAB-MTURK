import os

import pandas as pd

gvlab_dataset_path = '/Users/yonatab/PycharmProjects/GVLAB-backend/assets/gvlab_dataset.csv'
create_url = 'https://gvlab-dataset.github.io/mturk/create'
solve_url = 'https://gvlab-dataset.github.io/mturk/solve'

if __name__ == '__main__':
    df = pd.read_csv(gvlab_dataset_path)
    print(f"Read df: {len(df)}")
    df = df.sample(frac=1)
    for head in [100, 200, 500, 1000]:
        print(f"value counts top {head}")
        print(df['origin_candidates_number'].head(head).value_counts())
    create_urls = df['ID'].apply(lambda x: f"{create_url}/{x}")
    solve_urls = df['ID'].apply(lambda x: f"{solve_url}/{x}")
    create_urls.to_csv(os.path.join('urls','urls_create.csv'),index=False)
    solve_urls.to_csv(os.path.join('urls', 'urls_solve.csv'), index=False)
    print("Done")