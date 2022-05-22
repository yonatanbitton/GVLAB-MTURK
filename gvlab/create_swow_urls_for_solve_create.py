import os

import pandas as pd

# hit_type_id = '3K3YEJM751RRJS8ZW8AYJ5Y3VVB5WP' # create 0-100, double
# indices = 'indices_0_100'

# hit_type_id = '3HMIRIJYITY39Q6S35I504KLG4XRVE'  # create, 100-500
# indices = 'indices_100_500'

# hit_type_id = '325VGVP4D3PCDRAZVOXKTZLWGGX0L7'  # create random 0-100 - real
# indices = 'random_indices_0_100'

hit_type_id = '36ENCJ709KV0KB7BIVKYZOALLH2KEA'  # create random 100-250 - real
indices = 'random_indices_100_250'

created_data_path = f'created_data/create_hit_type_id_{hit_type_id}_{indices}.csv'

solve_url = 'https://gvlab-dataset.github.io/mturk/solve'

if __name__ == '__main__':
    df = pd.read_csv(created_data_path)
    print(f"Read df: {len(df)}")
    df = df.sample(frac=1)
    solve_urls = df['annotation_index'].apply(lambda x: f"{solve_url}/solve_create_{x}")
    out_p = os.path.join('urls', f'urls_solve_create_{hit_type_id}_{indices}.csv')
    print(f"Wrote df of {len(df)} associations to solve to {out_p}")
    solve_urls.to_csv(out_p, index=False)
    print("Done")