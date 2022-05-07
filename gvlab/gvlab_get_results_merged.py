import json

import pandas as pd
import os
import numpy as np

from gvlab.gvlab_swow import create_or_get_qualification, mturk


def main():
    # hit_type_id = '36R4ILE2GAQ1OZ6Z7L174EFT51AFHG'  # first test batch 0-100, private
    # hit_type_id = '3ABSYNXI57NPRZT5O7RK079PHQZMWU'  # 550-650, first public batch
    # hit_type_id = '34W4CI95J0NSJKQ6AHJ0UUUX2GUI9K'  # 100-550
    # hit_type_id = '3029CDJAWE2TGO6JR9IGKSJA2ZBDSO'  # 650-1200
    # hit_type_id = '3S942EFUVKZ59R1T0AKMY9A86SZJE7'  # 1200-1340
    all_hit_type_ids = ['36R4ILE2GAQ1OZ6Z7L174EFT51AFHG', '3ABSYNXI57NPRZT5O7RK079PHQZMWU', '34W4CI95J0NSJKQ6AHJ0UUUX2GUI9K', '3029CDJAWE2TGO6JR9IGKSJA2ZBDSO', '3S942EFUVKZ59R1T0AKMY9A86SZJE7']
    answers_data_df = pd.DataFrame()
    for hit_type_id in all_hit_type_ids:
        res_csv_path = os.path.join('results', f'results_hit_type_id_{hit_type_id}.csv')
        hit_type_id_df = pd.read_csv(res_csv_path)
        answers_data_df = pd.concat([answers_data_df, hit_type_id_df])

    for c in ['candidates', 'labels', 'user_predictions']:
        answers_data_df[c] = answers_data_df[c].apply(lambda x: json.loads(x.replace("'", '"').replace("{","[").replace("}","]")))
    print(f"# {len(answers_data_df)}, jaccard mean: {answers_data_df['jaccard'].mean()}")
    jaccard_per_user = get_results_by_user(answers_data_df)
    get_results_by_num_candidates(answers_data_df)
    all_mean_user_jaccard_for_association = get_user_agreement(answers_data_df)
    association_jaccard_threshold = 0.8
    associations_with_mean_jaccard_above_threshold = {k: v for k, v in all_mean_user_jaccard_for_association.items() if
                                                      v >= association_jaccard_threshold}
    print(f"{len(associations_with_mean_jaccard_above_threshold)}/{len(all_mean_user_jaccard_for_association)}")

    # create_swow_sample(associations_with_mean_jaccard_above_threshold)
    # update_and_notify_qualification(answers_data_df, jaccard_per_user)
    print("Done")


def update_and_notify_qualification(answers_data_df, jaccard_per_user):
    worker_ids = set(answers_data_df['WorkerId'].values)
    annotated_gvlab_swow_solve = {
        "Name": "First GVLAB Solve Batch Performance",
        "Description": "First GVLAB Solve Batch Performance",
        "QualificationTypeStatus": "Active",
        "AutoGranted": False,
    }
    annotated_gvlab_swow_solve_type_id = create_or_get_qualification(annotated_gvlab_swow_solve)
    update_qual_and_notify(annotated_gvlab_swow_solve_type_id, jaccard_per_user, worker_ids)


def update_qual_and_notify(annotated_gvlab_swow_solve_type_id, jaccard_per_user, worker_ids):
    for worker in worker_ids:
        worker_score = int(jaccard_per_user[worker] * 100)
        response_assign = mturk.associate_qualification_with_worker(
            QualificationTypeId=annotated_gvlab_swow_solve_type_id,  # the public qual
            WorkerId=worker,
            IntegerValue=worker_score,
            SendNotification=True
        )


def create_swow_sample(associations_with_mean_jaccard_above_threshold):
    final_swow_based = []
    for id in associations_with_mean_jaccard_above_threshold.keys():
        url = f'https://gvlab-dataset.github.io/mturk/solve/{id}'
        final_swow_based.append(url)
    final_swow_based_df = pd.DataFrame(final_swow_based)
    final_swow_based_df_sample = final_swow_based_df.sample(100)
    final_swow_based_df_sample.to_csv('urls/urls_final_swow_based_solve.csv')


def get_user_agreement(answers_data_df):
    df_by_id = answers_data_df.groupby('id')
    all_user_agreements = []
    all_mean_user_jaccard_for_association = {}
    for id, df_by_id in df_by_id:
        user1_preds = set(sorted(df_by_id['user_predictions'].iloc[0]))
        user2_preds = set(sorted(df_by_id['user_predictions'].iloc[1]))
        user3_preds = set(sorted(df_by_id['user_predictions'].iloc[2]))
        user_agreement_jaccard = len(user1_preds & user2_preds & user3_preds) / len(
            user1_preds | user2_preds | user3_preds)
        all_user_agreements.append(user_agreement_jaccard)

        user1_jaccard = df_by_id['jaccard'].iloc[0]
        user2_jaccard = df_by_id['jaccard'].iloc[1]
        user3_jaccard = df_by_id['jaccard'].iloc[2]
        mean_user_jaccard = np.mean([user1_jaccard, user2_jaccard, user3_jaccard])
        all_mean_user_jaccard_for_association[id] = mean_user_jaccard
    print(f"user agreement: {int(np.mean(all_user_agreements) * 100)}")
    print(f'mean jaccard for association: {int(np.mean(list(all_mean_user_jaccard_for_association.values())) * 100)}')
    return all_mean_user_jaccard_for_association


def get_results_by_num_candidates(answers_data_df):
    answers_data_df['num_candidates'] = answers_data_df['candidates'].apply(lambda x: len(x))
    df_by_num_candidates = answers_data_df.groupby('num_candidates')
    for num_candidates, num_candidates_df in df_by_num_candidates:
        print(f"num_candidates {num_candidates}, # items {len(num_candidates_df)} score: {int(num_candidates_df['jaccard'].mean() * 100)}")


def get_results_by_user(answers_data_df):
    df_by_users = answers_data_df.groupby('WorkerId')
    jaccard_per_user = {}
    for user, user_df in df_by_users:
        print(f"user {user}, # items: {len(user_df)} jaccard: {int(user_df['jaccard'].mean() * 100)}")
        jaccard_per_user[user] = user_df['jaccard'].mean()
    jaccard_per_user_values = list(jaccard_per_user.values())
    print(f"Mean jaccard per user: {int(np.mean(jaccard_per_user_values) * 100), int(np.median(jaccard_per_user_values) * 100)}")
    return jaccard_per_user

if __name__ == '__main__':
    main()