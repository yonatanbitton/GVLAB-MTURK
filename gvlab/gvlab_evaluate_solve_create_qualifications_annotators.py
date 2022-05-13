import json

import pandas as pd

from gvlab.gvlab_swow import mturk, create_or_get_qualification

user_collected_assocations_qualification_data_path = '/Users/yonatab/PycharmProjects/GVLAB-MTURK/gvlab/created_data/user_collected_associations_qualification.csv'
mean_jaccard_per_association_path = 'results/all_mean_user_jaccard_for_association_31UK836KROSS8RVV3KINI5EVNBTG3A.json'

def main():
    user_data = pd.read_csv(user_collected_assocations_qualification_data_path)
    mean_solvers_jaccard_per_association = json.load(open(mean_jaccard_per_association_path, 'r'))
    mean_solvers_jaccard_per_association_index = {int(k.split("_")[-1]):v for k,v in mean_solvers_jaccard_per_association.items()}
    user_data['mean_solvers_jaccard'] = user_data['annotation_index'].apply(lambda x: mean_solvers_jaccard_per_association_index[x] if x in mean_solvers_jaccard_per_association_index else -1)

    user_data_not_null = user_data[user_data['mean_solvers_jaccard'] != -1]
    print(f"Not null proportion: {len(user_data_not_null)}/{len(user_data)}")

    all_scores_for_workers = []
    for worker, worker_df in user_data.groupby('WorkerId'):
        mean_solver_jaccard = int(worker_df['mean_solvers_jaccard'].mean() * 100)
        mean_human_vs_model_jaccard = int(worker_df['score'].mean())
        minimum_score = min(mean_solver_jaccard, mean_human_vs_model_jaccard)
        all_scores_for_workers.append({'worker': worker, 'final_score': minimum_score, 'score_fooling_ai': mean_human_vs_model_jaccard, 'score_solvable_by_humans': mean_solver_jaccard})
    all_scores_for_workers_df = pd.DataFrame(all_scores_for_workers)
    min_score_fooling_ai = 35
    min_score_solvable_humans = 75
    proportion_fooling_ai = len(all_scores_for_workers_df[all_scores_for_workers_df['score_fooling_ai'] >= min_score_fooling_ai]) / len(all_scores_for_workers_df)
    proportion_solvable_by_humans = len(all_scores_for_workers_df[all_scores_for_workers_df['score_solvable_by_humans'] >= min_score_solvable_humans]) / len( all_scores_for_workers_df)
    passing_workers = all_scores_for_workers_df[all_scores_for_workers_df.apply(lambda x: x['score_fooling_ai'] >= min_score_fooling_ai and x['score_solvable_by_humans'] >= min_score_solvable_humans, axis=1)]
    amount_pass_joint_score = len(passing_workers)
    proportion_pass_joint_score = amount_pass_joint_score / len(all_scores_for_workers_df)
    print(f"proportion_fooling_ai: {proportion_fooling_ai}, proportion_solvable_by_humans: {proportion_solvable_by_humans}, proportion_pass_joint_score: {proportion_pass_joint_score}")

    # assign_qualification_and_notify(all_scores_for_workers_df, passing_workers)

    print("Done")


def assign_qualification_and_notify(all_scores_for_workers_df, passing_workers):
    passed_gvlab_create_qualification = {
        "Name": "passed_gvlab_create_qualification",
        "Description": "Passed the GVLAB create qualification",
        "QualificationTypeStatus": "Active",
        "AutoGranted": False,
    }
    passed_gvlab_create_qualification_type_id = create_or_get_qualification(passed_gvlab_create_qualification)
    num_passed = 0
    num_fail = 0
    failed_workers = []
    pass_responses = []
    pass_workers = []
    for r_idx, r in all_scores_for_workers_df.iterrows():
        passed = r_idx in passing_workers.index
        if passed:
            num_passed += 1
            worker_score = r['score_solvable_by_humans']
            response_assign = mturk.associate_qualification_with_worker(
                QualificationTypeId=passed_gvlab_create_qualification_type_id,  # the public qual
                WorkerId=r['worker'],
                IntegerValue=worker_score,
                SendNotification=True
            )
            pass_responses.append(response_assign)
            pass_workers.append(r['worker'])
        else:
            num_fail += 1
            failed_workers.append(r['worker'])
    SubjectPassed = 'GVLAB Create Qualification - Passed Successfully, Good Job!'
    MessageTextPassed = 'You did a great job. Only 20 people passed, which we hope will create thousands of new associations'
    SubjectFail = 'GVLAB Create Qualification - Did not pass'
    MessageTextFail = "Hello. You did not pass the create qualification test. Don't feel bad about it - this task is really subjective. There will be many solve HITs! Stay tuned!"
    response_success = mturk.notify_workers(Subject=SubjectPassed, MessageText=MessageTextPassed,
                                         WorkerIds=pass_workers)  # response['NotifyWorkersFailureStatuses']
    print(response_success)
    response_fail = mturk.notify_workers(Subject=SubjectFail, MessageText=MessageTextFail,
                                    WorkerIds=failed_workers)  # response['NotifyWorkersFailureStatuses']
    print(response_fail)
    print(f"num_passed: {num_passed}, num_fail: {num_fail}")
    print(f"Passed: {pass_workers}")
    print(f"Failed: {failed_workers}")


def get_proportion_pass_joint_score(all_scores_for_workers_df, min_score_fooling_ai, min_score_solvable_humans):
    pass_joint = len(all_scores_for_workers_df[all_scores_for_workers_df.apply(lambda x: x['score_fooling_ai'] >= min_score_fooling_ai and x['score_solvable_by_humans'] >= min_score_solvable_humans, axis=1)])
    proportion = pass_joint / len(all_scores_for_workers_df)
    return proportion

if __name__ == '__main__':
    main()