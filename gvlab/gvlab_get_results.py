import json
import os
import numpy as np
import pandas as pd
import xmltodict

from gvlab.example_gvlab_creation import review_hits
from gvlab.gvlab_get_results_merged_swow_solve import get_results_by_user, get_results_by_num_candidates, get_user_agreement
from gvlab.send_gvlab_tasks import mturk


def main(hit_type_id, approve=False):
    res_csv_path = os.path.join('results', f'results_hit_type_id_{hit_type_id}.csv')
    reviewed_hits = review_hits(hit_type_id)
    print(f"# Reviewed Hits: {len(reviewed_hits)}")
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
            answer_dict = get_annotation_data(answer_data, answer_dict)
            answers_data.append(answer_dict)
    if approve:
        print(f"Approved all ({num_approved}/{num_total}), exiting, hit_type_id: {hit_type_id}")
        return 0
    answers_data_df = pd.DataFrame(answers_data)
    is_create_task = False
    if 'jaccard' in answers_data_df.columns: # solve
        print(f"DF: {len(answers_data_df)}, # Associations: {len(reviewed_hits)}, jaccard mean: {answers_data_df['jaccard'].mean()}")
    elif 'score_fooling_ai_1' in answers_data_df.columns: # create
        is_create_task = True
        print(
            f"DF: {len(answers_data_df)}, # Associations: {len(reviewed_hits)}, score_fooling_ai_1: {answers_data_df['score_fooling_ai_1'].mean()}, score_fooling_ai_2: {answers_data_df['score_fooling_ai_2'].mean()}")
        workers_items = []
        for worker, worker_df in answers_data_df.groupby('WorkerId'):
            score_fooling_ai_1 = int(worker_df['score_fooling_ai_1'].mean())
            score_fooling_ai_2 = int(worker_df['score_fooling_ai_2'].mean())
            num_items = len(worker_df)
            workers_items.append({'worker': worker, 'num_items': num_items, 'score_fooling_ai_1': score_fooling_ai_1, 'score_fooling_ai_2': score_fooling_ai_2})
        workers_items_df = pd.DataFrame(workers_items)
        workers_items_df.sort_values(by=['score_fooling_ai_1'],inplace=True)
        print(workers_items_df)
    print(f"Dumped results to {res_csv_path}")
    answers_data_df.to_csv(res_csv_path)
    if is_create_task:
        print(f'*** is_create_task, breaking ***')
        return 0

    get_results_by_user(answers_data_df)

    get_results_by_num_candidates(answers_data_df)

    all_mean_user_jaccard_for_association, all_std_user_jaccard_for_association = get_user_agreement(answers_data_df)
    all_mean_user_jaccard_for_association_json_path = os.path.join('results', f'all_mean_user_jaccard_for_association_{hit_type_id}.json')
    print(f"Dumping json of len {len(all_mean_user_jaccard_for_association)} to {all_mean_user_jaccard_for_association_json_path}")
    json.dump(all_mean_user_jaccard_for_association, open(all_mean_user_jaccard_for_association_json_path, 'w'))

    all_std_user_jaccard_for_association_json_path = os.path.join('results',
                                                                   f'all_std_user_jaccard_for_association_{hit_type_id}.json')
    print(
        f"Dumping json of len {len(all_std_user_jaccard_for_association)} to {all_std_user_jaccard_for_association_json_path}")
    json.dump(all_std_user_jaccard_for_association, open(all_std_user_jaccard_for_association_json_path, 'w'))

    association_jaccard_threshold = 0.8
    associations_with_mean_jaccard_above_threshold = {k: v for k, v in all_mean_user_jaccard_for_association.items() if v >= association_jaccard_threshold}
    print(f"{len(associations_with_mean_jaccard_above_threshold)}/{len(all_mean_user_jaccard_for_association)}")
    print(f"Wrote to {res_csv_path}.")


def get_annotation_data(answer_data, answer_dict):
    if 'userCue' in answer_dict:
        selected_images_q1 = [x['img'].split("/")[-1] for x in answer_dict['candidates'][0] if x['userChoice']]
        selected_images_q2 = [x['img'].split("/")[-1] for x in answer_dict['candidates'][1] if x['userChoice']]
        score_fooling_ai_1 = answer_dict['score'][0]
        score_fooling_ai_2 = answer_dict['score'][1]
        cue1 = answer_dict['userCue'][0]
        cue2 = answer_dict['userCue'][1]
        all_candidates = [x['img'].split("/")[-1] for x in answer_dict['candidates'][0]]
        assert all_candidates == [x['img'].split("/")[-1] for x in answer_dict['candidates'][1]]
        answer_dict = {**answer_data, **{'id': answer_dict['id'], 'selected_images_q1': selected_images_q1, 'selected_images_q2': selected_images_q2,
                                         'score_fooling_ai_1': score_fooling_ai_1, 'score_fooling_ai_2': score_fooling_ai_2,'cue1': cue1, 'cue2': cue2, 'candidates': all_candidates}}
    else:
        labels = set([x['img'].split("/")[-1] for x in answer_dict['candidates'] if x['answer']])
        user_predictions = set([x['img'].split("/")[-1] for x in answer_dict['candidates'] if x['userChoice']])
        assert len(labels) == len(user_predictions)
        user_agreement_jaccard = len(labels.intersection(user_predictions)) / len(labels.union(user_predictions))
        all_candidates = [x['img'].split("/")[-1] for x in answer_dict['candidates']]
        answer_dict = {**answer_data, **{'id': answer_dict['id'], 'candidates': all_candidates, 'labels': labels,
                                         'user_predictions': user_predictions, 'jaccard': user_agreement_jaccard}}
    return answer_dict


if __name__ == '__main__':
    # hit_type_id = '3DCJP2JIFL2FRFFQ1YM56ARCF5J3C1' # sandbox 1
    # hit_type_id = '3U6Z1K5VYX5KJGIN25QFD2TZUVPN8V' # sandbox 2
    # hit_type_id = '36R4ILE2GAQ1OZ6Z7L174EFT51AFHG'  # first test batch 0-100, private
    # hit_type_id = '3ABSYNXI57NPRZT5O7RK079PHQZMWU'  # 550-650, first public batch
    # hit_type_id = '34W4CI95J0NSJKQ6AHJ0UUUX2GUI9K'  # 100-550
    # hit_type_id = '3029CDJAWE2TGO6JR9IGKSJA2ZBDSO'  # 650-1200
    # hit_type_id = '3S942EFUVKZ59R1T0AKMY9A86SZJE7' # 1200-1340
    # hit_type_id = '3DIFNAQ3LD1WDWH1NKHUHOTKD50T3V' # test solve
    # all_hits = ['36R4ILE2GAQ1OZ6Z7L174EFT51AFHG', '3ABSYNXI57NPRZT5O7RK079PHQZMWU', '34W4CI95J0NSJKQ6AHJ0UUUX2GUI9K', '3029CDJAWE2TGO6JR9IGKSJA2ZBDSO', '3S942EFUVKZ59R1T0AKMY9A86SZJE7', '3DIFNAQ3LD1WDWH1NKHUHOTKD50T3V']
    # hit_type_id = '31WLO1EP3YLN5XAOWVO1YNO5B0LQSN' # solve_create_qual_sandbox
    # hit_type_id = '31UK836KROSS8RVV3KINI5EVNBTG3A' # solve_create_qual - REAL
    # hit_type_id = '32TFGTUJLPQDB76DR6FYUGS8X6XPI3' # create 0-100 - sandbox
    # hit_type_id = '3K3YEJM751RRJS8ZW8AYJ5Y3VVB5WP' # create 0-100 - real
    # hit_type_id = '3VILS635XG325L99WI9CYIYV64ZSPY'  # solve-create 0-100 - sandbox
    # hit_type_id = '3PS3UFWQYLQKDK1X8G5P73OFYLZYRU'  # solve-create 0-100 - real
    # hit_type_id = '3HMIRIJYITY39Q6S35I504KLG4XRVE' # create-100-500 - real
    # hit_type_id = '3BKZR1PB4H0W7WEWCD111WG4U5X6KQ' # solve-create 100-300 - sandbox
    # hit_type_id = '3ES7ZYWJECSULNMPGJB6W8UQ8OKHC9'  # solve-create 100-300 - real
    # hit_type_id = '32A8IZJLQFI72Z2UI57PMZF56GCGHI'  # solve-create 300-500 - real
    # hit_type_id = '3IFS5X633EJJPFGUAK4DL676K769K7'  # create random 0-200 - snbbox
    # hit_type_id = '325VGVP4D3PCDRAZVOXKTZLWGGX0L7'   # create random 0-100 - real
    # hit_type_id = '3QY2P19FFIKAYHJVAD27T1ASL52XNJ' # solve-create random 0-100 - sandbox
    # hit_type_id = '30AWZEBKT3DFB0EBAD1EFM7MVTVCAU' # solve-create random 0-100 - real
    # hit_type_id = '36ENCJ709KV0KB7BIVKYZOALLH2KEA' # create random 100-250 - real
    # hit_type_id = '3ARIN4O78G41KUHJD3JTIME4V1DIFY' # solve create 100-250 - sandbox
    # hit_type_id = '359956SLTZK0DLUYP1GZDVMJP6XRLX'  # solve create 100-250 - real
    # hit_type_id = '3K9PHCH9NP5QQJXSW9O09AY34B5DGQ'  # game test - sandbox
    # hit_type_id = '3RL1BYM2927VU09ARQF3354OO0N97K' # game test - real
    # hit_type_id = '35RL0GHNS8FVIPBSS4ZKFSGO4N6GEM' # create random 10-12, 0-100, sandbox
    # hit_type_id = '30WQ7ZZ0RU9SNPFM4Z1FUITI23JH9U' # create random 10-12, 0-100 , real
    # hit_type_id = '3QY2P19FFIKAYHJVAD27T1ASL52XNJ' # solve create random 10-12, 0-100 , sandbox
    # hit_type_id = '3BIF6MRRHNW5YEAFVC7WMMY9VTJR8U' # solve create random 10-12, 0-100 , sandbox
    # hit_type_id = '30AWZEBKT3DFB0EBAD1EFM7MVTVCAU'  # solve create random 10-12, 0-100 , real
    hit_type_id = '33KTOXRB2MHEDTK23QD1IIHZSACFRH' # solve create random 10-12, 100-250 , real

    for hit_type_id in [hit_type_id]:
        approve = False
        print(f"approve: {approve}")
        main(hit_type_id, approve=approve)