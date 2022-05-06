import json
import os
import numpy as np
import pandas as pd
import xmltodict

from gvlab.example_gvlab_creation import review_hits


def main():
    # hit_type_id = '3DCJP2JIFL2FRFFQ1YM56ARCF5J3C1'
    # hit_type_id = '3U6Z1K5VYX5KJGIN25QFD2TZUVPN8V'
    hit_type_id = '36R4ILE2GAQ1OZ6Z7L174EFT51AFHG'  # first test batch
    res_csv_path = os.path.join('results', f'results_hit_type_id_{hit_type_id}.csv')
    reviewed_hits = review_hits(hit_type_id)
    print(f"# Reviewed Hits: {reviewed_hits}")
    answers_data = []
    for h in reviewed_hits:
        for h_assignment_dict in h:
            answer_data = {k: v for k,v in h_assignment_dict.items() if k in ['AssignmentId', 'WorkerId', 'HITId', 'AssignmentStatus']}
            answer_data['SubmitTime'] = h_assignment_dict['SubmitTime'].__str__()
            answer_dict = json.loads(xmltodict.parse(h_assignment_dict['Answer'])['QuestionFormAnswers']['Answer']['FreeText'])
            labels = set([x['img'].split("/")[-1] for x in answer_dict['candidates'] if x['answer']])
            user_predictions = set([x['img'].split("/")[-1] for x in answer_dict['candidates'] if x['userChoice']])
            assert len(labels) == len(user_predictions)
            jaccard = len(labels.intersection(user_predictions)) / len(labels.union(user_predictions))
            all_candidates = [x['img'].split("/")[-1] for x in answer_dict['candidates']]
            answer_dict = {**answer_data, **{'id': answer_dict['id'], 'candidates': all_candidates, 'labels': labels, 'user_predictions': user_predictions, 'jaccard': jaccard}}
            answers_data.append(answer_dict)
    answers_data_df = pd.DataFrame(answers_data)
    print(f"DF: {len(answers_data_df)}, jaccard mean: {answers_data_df['jaccard'].mean()}")
    answers_data_df.to_csv(res_csv_path)

    df_by_users = answers_data_df.groupby('WorkerId')
    for user, user_df in df_by_users:
        print(f"user {user} jaccard: {user_df['jaccard'].mean()}")

    answers_data_df['num_candidates'] = answers_data_df['candidates'].apply(lambda x: len(x))
    df_by_num_candidates = answers_data_df.groupby('num_candidates')
    for num_candidates, num_candidates_df in df_by_num_candidates:
        print(f"num_candidates {num_candidates} score: {num_candidates_df['jaccard'].mean()}")

    df_by_id = answers_data_df.groupby('id')
    all_user_agreements = []
    for id, df_by_id in df_by_id:
        user1_preds = set(sorted(df_by_id['user_predictions'].iloc[0]))
        user2_preds = set(sorted(df_by_id['user_predictions'].iloc[1]))
        user3_preds = set(sorted(df_by_id['user_predictions'].iloc[2]))
        jaccard = len(user1_preds & user2_preds & user3_preds) / len(user1_preds | user2_preds | user3_preds)
        all_user_agreements.append(jaccard)

    print(f"user agreement: {np.mean(all_user_agreements)}")
    print(f"Wrote to {res_csv_path}.")

if __name__ == '__main__':
    main()