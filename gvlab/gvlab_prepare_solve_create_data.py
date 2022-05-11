import os

import pandas as pd
import json

qual_csv = pd.read_csv('/Users/yonatab/PycharmProjects/GVLAB-backend/assets/gvlab_practice_and_qualification.csv')

def main():
    # create_data_qualification
    create_data_type = 'user_collected_associations_qualification'
    create_hits_type_ids = ['3ZT4KTA7QP12TXNO45XYG1KUDSO32E', '3U6Z1K5VYX5KJGIN25QEZ6V34978N2']

    out_p = os.path.join('created_data', f'{create_data_type}.csv')
    df = pd.DataFrame()
    for hit_type_id in create_hits_type_ids:
        hit_type_df = pd.read_csv(f'results/results_hit_type_id_{hit_type_id}.csv')
        df = pd.concat([df, hit_type_df])
    if "Unnamed: 0" in df.columns:
        df.drop(columns=["Unnamed: 0"], inplace=True)
    df['cue'] = df['userCue']
    df['associations'] = df['selected_images']
    df['candidates'] = df['id'].apply(lambda id: get_candidates_by_id(id, qual_csv))
    for c in ['associations', 'candidates']:
        df[c] = df[c].apply(lambda x: json.loads(x.replace("'",'"')))
    df['num_associations'] = df['associations'].apply(lambda x: len(x))
    for c in ['associations', 'candidates']:
        df[c] = df[c].apply(lambda x: json.dumps(x))
    print(f"Dumping df of len: {len(df)} to {out_p}")
    df.to_csv(out_p, index=False)

    print("Done")

def get_candidates_by_id(id, qual_csv):
    relevant_rows = qual_csv[qual_csv['ID'] == id]
    assert len(relevant_rows) == 1
    r = relevant_rows.iloc[0]
    candidates = r['candidates']
    return candidates

if __name__ == '__main__':
    main()