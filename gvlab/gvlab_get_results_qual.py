import json
import os
import pickle

import numpy as np
import pandas as pd
import xmltodict

from gvlab.example_gvlab_creation import review_hits
from gvlab.send_gvlab_tasks import mturk, create_or_get_qualification


def main(hit_type_id, approve):
    res_csv_path = os.path.join('results', f'results_hit_type_id_{hit_type_id}.csv')
    accepted_workers_csv_path = os.path.join('accepted_workers', f'results_hit_type_id_{hit_type_id}.csv')
    reviewed_hits = review_hits(hit_type_id)
    answers_data = []
    num_approved = 0
    num_total = 0
    is_create_task = False
    for h in reviewed_hits:
        for h_assignment_dict in h:
            num_total += 1
            if approve:
                if h_assignment_dict['AssignmentStatus'] == 'Submitted':
                    mturk.approve_assignment(AssignmentId=h_assignment_dict['AssignmentId'])
                    num_approved += 1
                continue
            answer_data = {k: v for k,v in h_assignment_dict.items() if k in ['AssignmentId', 'WorkerId', 'HITId', 'AssignmentStatus']}
            answer_data['SubmitTime'] = h_assignment_dict['SubmitTime'].__str__()
            general_answer_dict = json.loads(xmltodict.parse(h_assignment_dict['Answer'])['QuestionFormAnswers']['Answer']['FreeText'])
            personal_details = general_answer_dict['personalDetails']
            for answer_dict in general_answer_dict['tasks']:
                if 'userCue' in answer_dict:
                    is_create_task = True
                    assert len(answer_dict['candidates']) == 2
                    # selected_images_q1 = [x['img'].split("/")[-1] for x in answer_dict['candidates'][0] if x['answer']]
                    # selected_images_q2 = [x['img'].split("/")[-1] for x in answer_dict['candidates'][1] if x['answer']]
                    selected_images_q1 = [x['img'].split("/")[-1] for x in answer_dict['candidates'][0] if x['userChoice']]
                    selected_images_q2 = [x['img'].split("/")[-1] for x in answer_dict['candidates'][1] if x['userChoice']]
                    assert len(selected_images_q2) == 0
                    assert answer_dict['score'][1] is None
                    score = answer_dict['score'][0]
                    userCue = answer_dict['userCue'][0]
                    answer_dict = {**answer_data, **{'id': answer_dict['id'], 'selected_images': selected_images_q1, 'score': score, 'userCue': userCue, 'personal_details': personal_details}}
                else:
                    labels = set([x['img'].split("/")[-1] for x in answer_dict['candidates'] if x['answer']])
                    user_predictions = set([x['img'].split("/")[-1] for x in answer_dict['candidates'] if x['userChoice']])
                    assert len(labels) == len(user_predictions)
                    jaccard = len(labels.intersection(user_predictions)) / len(labels.union(user_predictions))
                    all_candidates = [x['img'].split("/")[-1] for x in answer_dict['candidates']]
                    answer_dict = {**answer_data, **{'id': answer_dict['id'], 'candidates': all_candidates, 'labels': labels, 'user_predictions': user_predictions, 'jaccard': jaccard, 'personal_details': personal_details}}
                answers_data.append(answer_dict)
    if approve:
        print(f"Approved all ({num_approved}/{num_total}), exiting, hit_type_id: {hit_type_id}")
        return 0
    answers_data_df = pd.DataFrame(answers_data)
    for c in ['selected_images', 'personal_details']:
        if c in answers_data_df:
            answers_data_df[c] = answers_data_df[c].apply(json.dumps)
    print(f"Dumped: {len(answers_data_df)} to {res_csv_path}")
    answers_data_df.to_csv(res_csv_path)
    if is_create_task:
        print(f'*** is_create_task, breaking ***')
        return 0
    print(f"DF: {len(answers_data_df)}, jaccard mean: {answers_data_df['jaccard'].mean()}")


    df_by_users = answers_data_df.groupby('WorkerId')
    accepted_users_items = []
    for user, user_df in df_by_users:
        assert len(set([str(x) for x in user_df['personal_details'].values])) == 1
        user_personal_details = json.loads(user_df['personal_details'].iloc[0])
        mean_jaccard = user_df['jaccard'].mean()
        print(f"user {user} jaccard: {user_df['jaccard'].mean()}")
        print(user_personal_details)
        if user_personal_details is None:
            user_personal_details = {}
        user_d = {**{'WorkerId': user, 'mean_jaccard': mean_jaccard}, **user_personal_details}
        accepted_users_items.append(user_d)
        print()
    accepted_users_df = pd.DataFrame(accepted_users_items)
    print(f"DF: {len(answers_data_df)}, jaccard mean: {answers_data_df['jaccard'].mean()}")
    print(f"Writing to {accepted_workers_csv_path}")
    accepted_users_df.to_csv(accepted_workers_csv_path)
    QUAL_SCORE_TO_PASS = 0.79
    # QUAL_SCORE_TO_PASS = 0.74
    # accepted_users_df[accepted_users_df['mean_jaccard'] >= QUAL_SCORE_TO_PASS]
    passed_df = accepted_users_df[accepted_users_df['mean_jaccard'] >= QUAL_SCORE_TO_PASS]
    print(accepted_users_df[['WorkerId', 'mean_jaccard']])
    passed_num = len(passed_df)
    pass_pct = passed_num / len(accepted_users_df)
    print(f'pass_number: {pass_pct} ({passed_num}/{len(accepted_users_df)})')
    print(passed_df[['WorkerId', 'mean_jaccard']])
    exit()

    users_qual_notifications_path = os.path.join('notifications', 'qual_notifications.pickle')
    if os.path.exists(users_qual_notifications_path):
        all_responses = pickle.load(open(users_qual_notifications_path, 'rb'))
        notified_workers = list(all_responses.keys())
    else:
        all_responses = {}
        notified_workers = []
    public_qual_passed_gvlab_solve_id = '3NDLUB5I81QKQQ3IP6QL8DLKB9C46U'
    Subject = 'GVLAB Qualification Test Results - Visual Association Task'
    for worker, score in accepted_users_df[['WorkerId','mean_jaccard']].values:
        if worker in notified_workers:
            print(f"Worker already notified: {worker}")
            continue
        print(f"Sending notification to worker: {worker}")
        score_int = int(score * 100)
        # MessageText_passed = f'Hello. You passed the qualification test (score: {score_int}). You can proceed to the full HITs, titled "GVLAB: Visual Associations - (solve items 550-650)". More will be available soon.'
        MessageText_passed = f'Hello. You passed the qualification test (score: {score_int}). We currently do not need new annotations, but HITs there will be more HITs next week.'
        MessageText_failed = f'Hello. You did not pass the qualification test (score: {score_int}). Thanks, we acknowledge that this task is subjective and not well-defined.'
        if score >= QUAL_SCORE_TO_PASS:
            response = mturk.notify_workers(Subject=Subject, MessageText=MessageText_passed, WorkerIds=[worker]) # response['NotifyWorkersFailureStatuses']
            response_assign = mturk.associate_qualification_with_worker(
                QualificationTypeId=public_qual_passed_gvlab_solve_id,  # the public qual
                WorkerId=worker,
                IntegerValue=score_int,
                SendNotification=True
            )
            resp_dict = {'response': response, 'response_assign': response_assign, 'passed': True}
        else:
            response = mturk.notify_workers(Subject=Subject, MessageText=MessageText_failed, WorkerIds=[worker])  # response['NotifyWorkersFailureStatuses']
            resp_dict = {'response': response, 'passed': False}
        print(f"{resp_dict}")
        all_responses[worker] = resp_dict

    print(f"Dumping all responses {len(all_responses)} to {users_qual_notifications_path}")
    pickle.dump(all_responses, open(users_qual_notifications_path, 'wb'))

    print("Done")


if __name__ == '__main__':
    # hit_type_id = '3DCJP2JIFL2FRFFQ1YM56ARCF5J3C1'
    # hit_type_id = '3R1N6HJI9CC5LHBKOVQ6EQSW77SWLH'
    # hit_type_id = '3J3XIOMSTTYANQ2TAL071JT4ZC0I08' # real qual
    # hit_type_id = '3PS3UFWQYLQKDK1X8G5P73OFYLYRYM'  # real qual public
    # hit_type_id = '3ZT4KTA7QP12TXNO45XYG1KUDSO32E'  # real qual private
    # all_hits = ['3J3XIOMSTTYANQ2TAL071JT4ZC0I08', '3PS3UFWQYLQKDK1X8G5P73OFYLYRYM', '3ZT4KTA7QP12TXNO45XYG1KUDSO32E']
    # create_hits_type_ids = ['3ZT4KTA7QP12TXNO45XYG1KUDSO32E', '3U6Z1K5VYX5KJGIN25QEZ6V34978N2']
    # sandbox_my_hit_type_id_create_qual = '3J1X5UP4FWI0OSEI7URW9Q24YALK5N'
    # create_hits_type_ids
    create_hits_type_ids = ['3EOS91U1V0YXXDK8CJJZ7OJBGZZBYX', '3EOS91U1V0YXXDK8CJJZ7OJBGZZBYX']
    for hit_type_id in create_hits_type_ids:
        approve = False
        print(f"approve: {approve}")
        main(hit_type_id, approve=approve)