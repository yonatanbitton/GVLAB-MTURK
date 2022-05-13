import os
from copy import deepcopy

import pandas as pd
import json

def main(hit_type_id):
    # create_data_qualification

    input_path = os.path.join('results', f'results_hit_type_id_{hit_type_id}.csv')
    out_p = os.path.join('created_data', f'create_hit_type_id_{hit_type_id}.csv')
    df = pd.read_csv(input_path)
    for c in ['selected_images_q1', 'selected_images_q2', 'candidates']:
        df[c] = df[c].apply(lambda x: json.loads(x.replace("'",'"')))
    if "Unnamed: 0" in df.columns:
        df.drop(columns=["Unnamed: 0"], inplace=True)

    solve_create_items = []
    for r_idx, r in df.iterrows():
        r_dict = r.to_dict()
        set_cue_and_associations(r, r_dict, cue_idx=1)
        solve_create_items.append(deepcopy(r_dict))
        set_cue_and_associations(r, r_dict, cue_idx=2)
        solve_create_items.append(deepcopy(r_dict))

    solve_create_items_df = pd.DataFrame(solve_create_items)
    solve_create_items_df['associations_str'] = solve_create_items_df['associations'].apply(lambda x: str(sorted(x)))
    solve_create_items_df['associations'] = solve_create_items_df['associations'].apply(lambda lst: [x.split(".")[0] for x in lst])
    solve_create_items_df['num_associations'] = solve_create_items_df['associations'].apply(lambda x: len(x))
    for c in ['associations', 'candidates', 'selected_images_q1', 'selected_images_q2']:
        solve_create_items_df[c] = solve_create_items_df[c].apply(lambda x: json.dumps(x))
    print(f"Dumping df of len: {len(df)} to {out_p}")
    solve_create_items_df['annotation_index'] = range(len(solve_create_items_df))
    solve_create_items_df.to_csv(out_p, index=False)

    print("Done")


def set_cue_and_associations(r, r_dict, cue_idx):
    associations = r[f'selected_images_q{cue_idx}']
    cue = r[f'cue{cue_idx}']
    r_dict['cue'] = cue
    r_dict['associations'] = associations
    return r_dict


def get_candidates_by_id(id, qual_csv):
    relevant_rows = qual_csv[qual_csv['ID'] == id]
    assert len(relevant_rows) == 1
    r = relevant_rows.iloc[0]
    candidates = r['candidates']
    return candidates

if __name__ == '__main__':
    hit_type_id = '3K3YEJM751RRJS8ZW8AYJ5Y3VVB5WP'
    main(hit_type_id)