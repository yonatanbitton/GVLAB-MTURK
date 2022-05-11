import json
import os
import numpy as np
import pandas as pd
import xmltodict

from gvlab.example_gvlab_creation import review_hits
from gvlab.gvlab_get_results_merged import get_results_by_user, get_results_by_num_candidates, get_user_agreement
from gvlab.gvlab_swow import mturk


def main(hit_type_id, approve=False):
    res_csv_path = os.path.join('results', f'results_hit_type_id_{hit_type_id}.csv')
    reviewed_hits = review_hits(hit_type_id)
    print(f"# Reviewed Hits: {reviewed_hits}")
    num_approved = 0
    num_total = 0
    answers_data = []
    for h in reviewed_hits:
        for h_assignment_dict in h:
            num_total += 1
            if approve:
                if h_assignment_dict['AssignmentStatus'] == 'Submitted':
                    mturk.approve_assignment(AssignmentId=h_assignment_dict['AssignmentId'])
                    num_approved += 1
                else:
                    print(h_assignment_dict['AssignmentStatus'])
                continue
            answer_data = {k: v for k,v in h_assignment_dict.items() if k in ['AssignmentId', 'WorkerId', 'HITId', 'AssignmentStatus']}
            answer_data['SubmitTime'] = h_assignment_dict['SubmitTime'].__str__()
            answer_dict = json.loads(xmltodict.parse(h_assignment_dict['Answer'])['QuestionFormAnswers']['Answer']['FreeText'])
            labels = set([x['img'].split("/")[-1] for x in answer_dict['candidates'] if x['answer']])
            user_predictions = set([x['img'].split("/")[-1] for x in answer_dict['candidates'] if x['userChoice']])
            assert len(labels) == len(user_predictions)
            user_agreement_jaccard = len(labels.intersection(user_predictions)) / len(labels.union(user_predictions))
            all_candidates = [x['img'].split("/")[-1] for x in answer_dict['candidates']]
            answer_dict = {**answer_data, **{'id': answer_dict['id'], 'candidates': all_candidates, 'labels': labels, 'user_predictions': user_predictions, 'jaccard': user_agreement_jaccard}}
            answers_data.append(answer_dict)
    if approve:
        print(f"Approved all ({num_approved}/{num_total}), exiting, hit_type_id: {hit_type_id}")
        return 0
    answers_data_df = pd.DataFrame(answers_data)
    print(f"DF: {len(answers_data_df)}, # Associations: {len(reviewed_hits)}, jaccard mean: {answers_data_df['jaccard'].mean()}")
    answers_data_df.to_csv(res_csv_path)

    get_results_by_user(answers_data_df)

    get_results_by_num_candidates(answers_data_df)

    all_mean_user_jaccard_for_association = get_user_agreement(answers_data_df)

    association_jaccard_threshold = 0.8
    associations_with_mean_jaccard_above_threshold = {k: v for k, v in all_mean_user_jaccard_for_association.items() if v >= association_jaccard_threshold}
    print(f"{len(associations_with_mean_jaccard_above_threshold)}/{len(all_mean_user_jaccard_for_association)}")
    print(f"Wrote to {res_csv_path}.")



if __name__ == '__main__':
    # hit_type_id = '3DCJP2JIFL2FRFFQ1YM56ARCF5J3C1' # sandbox 1
    # hit_type_id = '3U6Z1K5VYX5KJGIN25QFD2TZUVPN8V' # sandbox 2
    # hit_type_id = '36R4ILE2GAQ1OZ6Z7L174EFT51AFHG'  # first test batch 0-100, private
    # hit_type_id = '3ABSYNXI57NPRZT5O7RK079PHQZMWU'  # 550-650, first public batch
    # hit_type_id = '34W4CI95J0NSJKQ6AHJ0UUUX2GUI9K'  # 100-550
    # hit_type_id = '3029CDJAWE2TGO6JR9IGKSJA2ZBDSO'  # 650-1200
    # hit_type_id = '3S942EFUVKZ59R1T0AKMY9A86SZJE7' # 1200-1340
    # hit_type_id = '3DIFNAQ3LD1WDWH1NKHUHOTKD50T3V' # test solve
    all_hits = ['36R4ILE2GAQ1OZ6Z7L174EFT51AFHG', '3ABSYNXI57NPRZT5O7RK079PHQZMWU', '34W4CI95J0NSJKQ6AHJ0UUUX2GUI9K', '3029CDJAWE2TGO6JR9IGKSJA2ZBDSO', '3S942EFUVKZ59R1T0AKMY9A86SZJE7', '3DIFNAQ3LD1WDWH1NKHUHOTKD50T3V']
    for hit_type_id in all_hits:
        approve = True
        print(f"approve: {approve}")
        main(hit_type_id, approve=approve)