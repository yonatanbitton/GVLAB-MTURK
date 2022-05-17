import json

import pandas as pd

from gvlab.send_gvlab_tasks import mturk, create_or_get_qualification

user_collected_assocations_qualification_data_path = 'created_data/user_collected_associations_qualification.csv'
mean_jaccard_per_association_path = 'results/all_mean_user_jaccard_for_association_31UK836KROSS8RVV3KINI5EVNBTG3A.json'


def calc_bonus(score_fool_ai, score_solvable_by_humans):
    # Base payment 0.07$
    if score_solvable_by_humans < 0.8 or score_fool_ai < 50:
        return 0
    if 50 <= score_fool_ai < 60:
        return 0.03  # total - 0.08$ (+0.03$)
    elif 60 <= score_fool_ai < 67:
        return 0.07  # total - 0.12$ (+0.04$)
    elif 67 <= score_fool_ai < 80:
        return 0.12  # total - 0.17$ (+0.05$)
    elif 80 <= score_fool_ai:
        return 0.18  # total - 0.23$ (+0.06$)
    else:
        raise Exception(f"Unexpected scores: {score_fool_ai}, {score_solvable_by_humans}")



def main():
    user_data = pd.read_csv(user_collected_assocations_qualification_data_path)
    user_data['num_candidates'] = user_data['candidates'].apply(lambda x: len(json.loads(x)))
    mean_solvers_jaccard_per_association = json.load(open(mean_jaccard_per_association_path, 'r'))
    mean_solvers_jaccard_per_association_index = {int(k.split("_")[-1]):v for k,v in mean_solvers_jaccard_per_association.items()}
    user_data['mean_solvers_jaccard'] = user_data['annotation_index'].apply(lambda x: mean_solvers_jaccard_per_association_index[x] if x in mean_solvers_jaccard_per_association_index else -1)

    user_data['bonus'] = user_data.apply(lambda r: calc_bonus(r['score'], r['mean_solvers_jaccard']), axis=1)

    user_data_not_null = user_data[user_data['mean_solvers_jaccard'] != -1]
    print(f"Not null proportion: {len(user_data_not_null)}/{len(user_data)}")

    all_scores_for_workers = []
    for worker, worker_df in user_data.groupby('WorkerId'):
        # for num_associations, worker_num_associations_df in worker_df.groupby('num_associations'):
        #     for num_candidates, worker_num_candidates_df in worker_num_associations_df.groupby('num_candidates'):
        #         num_associations = worker_num_candidates_df['num_associations'].mean()
        #         mean_solver_jaccard = int(worker_num_candidates_df['mean_solvers_jaccard'].mean() * 100)
        #         mean_human_vs_model_jaccard = int(worker_num_candidates_df['score'].mean())
        #         minimum_score = min(mean_solver_jaccard, mean_human_vs_model_jaccard)
        #         all_scores_for_workers.append(
        #             {'worker': worker, 'final_score': minimum_score, 'score_fooling_ai': mean_human_vs_model_jaccard,
        #              'score_solvable_by_humans': mean_solver_jaccard, 'num_associations': num_associations, 'num_candidates': num_candidates})
        num_associations = worker_df['num_associations'].mean()
        mean_solver_jaccard = int(worker_df['mean_solvers_jaccard'].mean() * 100)
        mean_human_vs_model_jaccard = int(worker_df['score'].mean())
        median_solver_jaccard = int(worker_df['mean_solvers_jaccard'].median() * 100)
        median_human_vs_model_jaccard = int(worker_df['score'].median())
        bonus_mean = worker_df['bonus'].mean()
        bonus_median = worker_df['bonus'].median()
        minimum_score = min(mean_solver_jaccard, mean_human_vs_model_jaccard)
        all_scores_for_workers.append({'worker': worker, 'final_score': minimum_score, 'score_fooling_ai': mean_human_vs_model_jaccard, 'score_solvable_by_humans': mean_solver_jaccard, 'num_associations': num_associations, 'median_solver_jaccard': median_solver_jaccard, 'median_human_vs_model_jaccard': median_human_vs_model_jaccard, 'bonus_mean': bonus_mean, 'bonus_median': bonus_median})
    all_scores_for_workers_df = pd.DataFrame(all_scores_for_workers)
    """
    all_scores_for_workers_df[all_scores_for_workers_df['num_associations'] == 2].mean()
    all_scores_for_workers_df[all_scores_for_workers_df['num_associations'] == 3].mean()
    all_scores_for_workers_df[all_scores_for_workers_df['num_associations'] == 4].mean()
    """
    min_score_fooling_ai = 35
    min_score_solvable_humans = 75
    proportion_fooling_ai = len(all_scores_for_workers_df[all_scores_for_workers_df['score_fooling_ai'] >= min_score_fooling_ai]) / len(all_scores_for_workers_df)
    proportion_solvable_by_humans = len(all_scores_for_workers_df[all_scores_for_workers_df['score_solvable_by_humans'] >= min_score_solvable_humans]) / len( all_scores_for_workers_df)
    passing_workers = all_scores_for_workers_df[all_scores_for_workers_df.apply(lambda x: x['score_fooling_ai'] >= min_score_fooling_ai and x['score_solvable_by_humans'] >= min_score_solvable_humans, axis=1)]
    amount_pass_joint_score = len(passing_workers)
    proportion_pass_joint_score = amount_pass_joint_score / len(all_scores_for_workers_df)
    print(f"proportion_fooling_ai: {proportion_fooling_ai}, proportion_solvable_by_humans: {proportion_solvable_by_humans}, proportion_pass_joint_score: {proportion_pass_joint_score}")

    # assign_qualification_and_notify(all_scores_for_workers_df, passing_workers)
    # notify_scores_explaination(passing_workers)
    response = notify_batch(passing_workers)
    print(response)
    print("Done")


def notify_batch(passing_workers):
    SubjectBatchIsAvailable = 'First "create" batch is available: "GVLAB: Visual Associations - (create items 0-100)"'
    MessageBatchAvailable = "You are welcome to solve it. Please ask via mail if something is unclear." \
                            "Make sure you understand the reward system! It is written in the description of the HIT. Good luck :)"
    response = mturk.notify_workers(Subject=SubjectBatchIsAvailable, MessageText=MessageBatchAvailable,
                                    WorkerIds=list(passing_workers['worker']))
    return response


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

def notify_scores_explaination(passing_workers):
    SubjectPassed = 'GVLAB create qualification: scores of fooling-the-AI, and solvable by humans'
    BaseMessage = "You receive this message because you have passed the 'create' qualification (Yay!). Create HITs will be published soon, and we now explain about our scoring system - it effects your bonus rewards."
    all_responses = []
    for r_idx, r in passing_workers.iterrows():
        # if r_idx < 11:
        #     continue
        if r_idx not in [11, 23, 26, 27, 29]:
            continue
        score_solvable_by_humans = r['score_solvable_by_humans']
        score_fooling_ai = r['score_fooling_ai']
        message_reward = f"\n Your average score for fooling the AI is {score_fooling_ai}, and the average score of solvable by humans is {score_solvable_by_humans}." \
                         f"\n A 'fool-the-AI' score can range from 0 (AI wasn't fooled at all) to 50, 60, 66, 80, 100 (AI didn't succeed at anything)." \
                         f"\n A generous bonus will be awarded to those who receive a high 'fool-the-AI' score, but still keep the association solvable by humans." \
                         f"\n Stay tuned to the 'create' HITs, there are only 20 creators, and you are one of the :)" \
                         f"\n Please reach out if you have any questions"
        BaseMessage += '\n' + message_reward
        try:
            response = mturk.notify_workers(Subject=SubjectPassed, MessageText=BaseMessage,
                                                    WorkerIds=[r['worker']])  # response['NotifyWorkersFailureStatuses']
            print(response)
        except Exception as ex:
            print(f"Exception r_idx: {r_idx}")
            continue
        all_responses.append(response)
        print("Done worker")
    print("Done worker")


def get_proportion_pass_joint_score(all_scores_for_workers_df, min_score_fooling_ai, min_score_solvable_humans):
    pass_joint = len(all_scores_for_workers_df[all_scores_for_workers_df.apply(lambda x: x['score_fooling_ai'] >= min_score_fooling_ai and x['score_solvable_by_humans'] >= min_score_solvable_humans, axis=1)])
    proportion = pass_joint / len(all_scores_for_workers_df)
    return proportion

if __name__ == '__main__':
    main()