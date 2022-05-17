import os
from copy import deepcopy

import pandas as pd
import json

from tqdm import tqdm

gvlab_swow_annotations_path = os.path.join('results', 'swow_with_jaccard_items_df.csv')
gvlab_swow_annotations = pd.read_csv(gvlab_swow_annotations_path)
gvlab_swow_annotations['associations'] = gvlab_swow_annotations['associations'].apply(json.loads)

def main(hit_type_id, indices):
    # create_data_qualification

    input_path = os.path.join('results', f'results_hit_type_id_{hit_type_id}.csv')
    out_p = os.path.join('created_data', f'create_hit_type_id_{hit_type_id}_{indices}.csv')
    df = pd.read_csv(input_path)
    for c in ['selected_images_q1', 'selected_images_q2', 'candidates']:
        df[c] = df[c].apply(lambda x: json.loads(x.replace("'",'"')))
    if "Unnamed: 0" in df.columns:
        df.drop(columns=["Unnamed: 0"], inplace=True)

    solve_create_items = []
    for r_idx, r in tqdm(df.iterrows(), desc='iterating', total=len(df)):
        r_dict = r.to_dict()
        r_dict['candidates'] = [x.split(".jpg")[0] for x in r_dict['candidates']]
        add_cue_and_associations(r, r_dict, solve_create_items, cue_idx=1)
        add_cue_and_associations(r, r_dict, solve_create_items, cue_idx=2)

    solve_create_items_df = pd.DataFrame(solve_create_items)

    for id, id_df in solve_create_items_df.groupby('id'):
        if len(set(id_df['cue'])) < 6:
            print(id)
            print(id_df[['cue', 'associations']])
            print()

    # solve_create_items_df['associations_str'] = solve_create_items_df['associations'].apply(lambda x: str(sorted(x)))
    solve_create_items_df['associations'] = solve_create_items_df['associations'].apply(lambda lst: [x.split(".")[0] for x in lst])
    solve_create_items_df['num_associations'] = solve_create_items_df['associations'].apply(lambda x: len(x))
    for c in ['associations', 'candidates', 'selected_images_q1', 'selected_images_q2']:
        solve_create_items_df[c] = solve_create_items_df[c].apply(lambda x: json.dumps(x))
    print(f"Dumping df of len: {len(solve_create_items_df)} to {out_p}")
    solve_create_items_df['annotation_index'] = range(len(solve_create_items_df))
    solve_create_items_df.to_csv(out_p, index=False)

    print("Done")


def add_cue_and_associations(r, r_dict, solve_create_items, cue_idx):
    associations = r[f'selected_images_q{cue_idx}']
    cue = r[f'cue{cue_idx}']
    score = r[f'score_fooling_ai_{cue_idx}']
    r_dict['cue'] = cue
    r_dict['associations'] = associations
    r_dict['score'] = score
    swow_rows = gvlab_swow_annotations[gvlab_swow_annotations['ID'] == r_dict['id']]
    # assert len(swow_rows) ==
    swow_row_exists = False
    if len(swow_rows) == 0:
        print("MISSING SWOW ROW!")
        swow_row = False
    else:
        swow_row = swow_rows.iloc[0]
        swow_row_exists = True
    r_dict_associations_no_jpg = sorted([x.split(".jpg")[0] for x in r_dict['associations']])

    # FILTER EXISTING DATA
    existing_data_for_id = [x for x in solve_create_items if x['id'] == r_dict['id']]
    for item in existing_data_for_id:
        if item['cue'] == cue and item['associations'] == associations:
            # print("Duplicate data, not adding")
            print("Duplicate data")
            # return 0

    solve_create_items.append(deepcopy(r_dict))

    # FILTER SWOW DATA
    if swow_row_exists and r_dict['cue'] == swow_row['cue'] and r_dict_associations_no_jpg == sorted(swow_row['associations']):
        print("*** SAME as SWOW")
        print((r_dict['cue'], r_dict_associations_no_jpg))
        solvers_mean_jaccard = swow_row['solvers_mean_jaccard']
        # solve_create_items.append(deepcopy(r_dict)) # adding anyway... ?
    elif swow_row_exists and (r_dict['cue'] == swow_row['cue'] or r_dict_associations_no_jpg == swow_row['associations']):
        print("*** SIMILAR to SWOW")
        print(f"r: {r_dict['cue']}, swow: {swow_row['cue']}, r: {r_dict_associations_no_jpg}, swow: {swow_row['associations']}")
        # solve_create_items.append(deepcopy(r_dict))
    # else:
    #     solve_create_items.append(deepcopy(r_dict))


def get_candidates_by_id(id, qual_csv):
    relevant_rows = qual_csv[qual_csv['ID'] == id]
    assert len(relevant_rows) == 1
    r = relevant_rows.iloc[0]
    candidates = r['candidates']
    return candidates

if __name__ == '__main__':
    # hit_type_id = '3K3YEJM751RRJS8ZW8AYJ5Y3VVB5WP'  # create, 0-100
    # indices = 'indices_0_100'
    hit_type_id = '3HMIRIJYITY39Q6S35I504KLG4XRVE' # create, 100-500
    indices = 'indices_100_500'
    main(hit_type_id, indices)