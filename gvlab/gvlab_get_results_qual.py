import json
import os
import numpy as np
import pandas as pd
import xmltodict

from gvlab.example_gvlab_creation import review_hits


def main():
    # hit_type_id = '3DCJP2JIFL2FRFFQ1YM56ARCF5J3C1'
    hit_type_id = '3R1N6HJI9CC5LHBKOVQ6EQSW77SWLH'
    res_csv_path = os.path.join('results', f'results_hit_type_id_{hit_type_id}.csv')
    accepted_workers_csv_path = os.path.join('accepted_workers', f'results_hit_type_id_{hit_type_id}.csv')
    reviewed_hits = review_hits(hit_type_id)
    answers_data = []
    for h in reviewed_hits:
        for h_assignment_dict in h:
            answer_data = {k: v for k,v in h_assignment_dict.items() if k in ['AssignmentId', 'WorkerId', 'HITId', 'AssignmentStatus']}
            answer_data['SubmitTime'] = h_assignment_dict['SubmitTime'].__str__()
            general_answer_dict = json.loads(xmltodict.parse(h_assignment_dict['Answer'])['QuestionFormAnswers']['Answer']['FreeText'])
            personal_details = general_answer_dict['personalDetails']
            for answer_dict in general_answer_dict['tasks']:
                labels = set([x['img'].split("/")[-1] for x in answer_dict['candidates'] if x['answer']])
                user_predictions = set([x['img'].split("/")[-1] for x in answer_dict['candidates'] if x['userChoice']])
                assert len(labels) == len(user_predictions)
                jaccard = len(labels.intersection(user_predictions)) / len(labels.union(user_predictions))
                all_candidates = [x['img'].split("/")[-1] for x in answer_dict['candidates']]
                answer_dict = {**answer_data, **{'id': answer_dict['id'], 'candidates': all_candidates, 'labels': labels, 'user_predictions': user_predictions, 'jaccard': jaccard, 'personal_details': personal_details}}
                answers_data.append(answer_dict)
    answers_data_df = pd.DataFrame(answers_data)
    print(f"DF: {len(answers_data_df)}, jaccard mean: {answers_data_df['jaccard'].mean()}")
    answers_data_df.to_csv(res_csv_path)

    df_by_users = answers_data_df.groupby('WorkerId')
    accepted_users_items = []
    for user, user_df in df_by_users:
        assert len(set([str(x) for x in user_df['personal_details'].values])) == 1
        user_personal_details = user_df['personal_details'].iloc[0]
        mean_jaccard = user_df['jaccard'].mean()
        print(f"user {user} jaccard: {user_df['jaccard'].mean()}")
        print(user_personal_details)
        user_d = {**{'WorkerId': user, 'mean_jaccard': mean_jaccard}, **user_personal_details}
        accepted_users_items.append(user_d)
        print()
    accepted_users_df = pd.DataFrame(accepted_users_items)
    print(f"DF: {len(answers_data_df)}, jaccard mean: {answers_data_df['jaccard'].mean()}")
    print(f"Writing to {accepted_workers_csv_path}")
    accepted_users_df.to_csv(accepted_workers_csv_path)
    print("Done")


if __name__ == '__main__':
    main()