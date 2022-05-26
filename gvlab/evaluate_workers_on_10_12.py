import json
import pandas as pd

from gvlab.gvlab_get_results_merged_swow_solve import get_results_by_user

if __name__ == '__main__':
    df = pd.read_csv('gvlab/results/results_hit_type_id_30AWZEBKT3DFB0EBAD1EFM7MVTVCAU.csv')
    df['candidates_num'] = df['candidates'].apply(lambda x: len(json.loads(x.replace("'",'"'))))
    print(f"Before")
    print(df['candidates_num'].value_counts())
    print('Taking only 10-12')
    df = df[df['candidates_num'].isin([10,12])]
    print(f"Jaccard: {df['jaccard'].mean()}")
    print('Taking only 10-12')
    print(df['candidates_num'].value_counts())
    get_results_by_user(df)