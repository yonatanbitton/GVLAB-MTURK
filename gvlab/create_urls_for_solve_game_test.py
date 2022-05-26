import os

import pandas as pd

gvlab_dataset_path = '/Users/yonatab/PycharmProjects/GVLAB-backend/assets/gvlab_game_split.csv'
solve_url = 'https://gvlab-dataset.github.io/mturk/solve'

if __name__ == '__main__':
    df = pd.read_csv(gvlab_dataset_path)
    print(f"Read df: {len(df)}")
    df = df.sample(frac=1).sample(int(len(df) / 10))
    print(f"Sampled {len(df)} items")
    solve_urls = df['ID'].apply(lambda x: f"{solve_url}/solve_game_test_{x}")
    solve_urls.to_csv(os.path.join('urls', 'urls_solve_game_test.csv'), index=False)
    print("Done")